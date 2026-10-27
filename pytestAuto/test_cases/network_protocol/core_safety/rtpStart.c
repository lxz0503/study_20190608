/* rtpStart.c - only used for test ipnet support CORE SAFETY */

/*
 * Copyright (c) 1988-2018, 2020-2021 Wind River Systems, Inc.
 *
 * The right to copy, distribute, modify or otherwise make use
 * of this software may be licensed only pursuant to the terms
 * of an applicable Wind River license agreement.
 */

/* includes */

#include "vxWorks.h"
#include <vxWorks.h>
#include <stdio.h>
#include <clockLib.h> 
#include <taskLib.h> 
#include <rtpLib.h>      /* CORE_SAFETY layer*/
#include <rtpPartLib.h> /* CORE_SAFETY layer */ 
#include <timePartLib.h> /* CORE_SAFETY layer */ 
#include <resAllocCtrlLib.h> 

#define TEST_RTP_NAME "/romfs/rtp.vxe"

#ifdef _WRS_CONFIG_MIMALLOC
#ifdef _WRS_CONFIG_LP64
/* With MIMALLOC, each RTP requires >4MB memory */
#define TEST_RTP_HEAP_LIMIT (1024 * 1024 * 5)
#else
/* With MIMALLOC, each RTP requires >2MB memory */
#define TEST_RTP_HEAP_LIMIT (1024 * 1024 * 3)
#endif
#else
#define TEST_RTP_HEAP_LIMIT (1024 * 1024)
#endif

LOCAL _Vx_rtp_cfg_t rtpCfg[] = 
    {
    {TEST_RTP_NAME, 0} 
    };
  
LOCAL _Vx_ptw_cfg_t ptwCfg[] =
    {
    {1, "0", 0, NULL,                      
     10, TIME_PART_ALLOW_KERNEL_TASKS
    }
    };

LOCAL _Vx_res_alloc_cfg_t resAllocCfg[] =
    {
    /* HEAP allocation      SHARED MEMORY region */
    {TEST_RTP_HEAP_LIMIT,                0}
    };

LOCAL _Vx_ptw_sched_id_t schedId;
LOCAL RTP_ID             rtpId;

LOCAL void Pause
    ( 
    time_t tv_sec 
    )
    {
    const struct timespec SleepInterval = {tv_sec, 0};
    struct timespec       TimeRemaining = {0, 0};
    
    printf( "Pause[%0x(s)]\n", tv_sec );
    
    clock_nanosleep (CLOCK_REALTIME, 0, &SleepInterval, &TimeRemaining);
    }  
          
LOCAL void CPUAffinitySet
    ( 
    int Index 
    )
    {
    cpuset_t TaskAffinityCPUSet;     // Presently only one CPU in set
    TASK_ID  ThisTaskId;
    cpuset_t ReservedCPUSet = 0;

    printf ("\nentered CPUAffinitySet...\n");
    
    ThisTaskId = taskIdSelf();
    printf ("ThisTaskId[0x%0x]\n", ThisTaskId);
    Pause ((time_t)1);
    taskShow (ThisTaskId, 1);
    
    // Initialize CPUSet with the desired CPU
    CPUSET_ZERO (TaskAffinityCPUSet);
    CPUSET_SET (TaskAffinityCPUSet, Index);
    
    printf ("CPUAffinitySet: call vxCpuUnreserve..." );
    if (vxCpuUnreserve( TaskAffinityCPUSet ) == OK)
        printf( " OK\n" );
    else
        printf( " *FAILED*\n" );
    
    printf ("CPUAffinitySet: call taskCpuAffinitySet...");
    if (taskCpuAffinitySet( ThisTaskId, TaskAffinityCPUSet ) == OK)
        printf (" OK\n");
    else
        printf (" *FAILED*\n");
          
    Pause ((time_t)1);
    taskShow (ThisTaskId, 1);

    printf ("CPUAffinitySet: call vxCpuReserve...");
    if (vxCpuReserve( TaskAffinityCPUSet, &ReservedCPUSet ) == OK)
        printf (" OK\n");
    else
        printf (" *FAILED* ReservedCPUSet[0x%0x]\n", ReservedCPUSet);
    
    printf ("\n...exiting CPUAffinitySet\n");
    } 
        
STATUS ATestSPRTP 
    (
    char * server,
    char * ipaddr,
    char * loop
    )
    {
    int prio;
    const char * pRtpArgs [] = {TEST_RTP_NAME, server, ipaddr, loop, NULL};
    
    printf ("ATestSPRTP: call rtpPartListInit... ");
    
    if (rtpPartListInit (&rtpCfg[0], NELEMENTS(rtpCfg)) != OK)
        {
        printf ("*FAILED*\n");
        return ERROR;
	}
    printf ("*OK*\n");
    
    /*
     * Create a time partition schedule.
     */
    
    printf ("ATestSPRTP: call timePartScheduleCreate... ");
    schedId = timePartScheduleCreate (&ptwCfg[0], NELEMENTS(ptwCfg));
    
    if (schedId == -1)
        {
        printf ("ATestSPRTP: timePartScheduleCreate *FAILED*\n" );
        return ERROR;
        }  
    printf ("OK, schedId[%d]\n", schedId);
    
    printf ("ATestSPRTP: call resAllocCtrlConfigure... " );
    if (resAllocCtrlConfigure(&resAllocCfg[0], NELEMENTS(resAllocCfg)) != OK)
        {
        printf( "*FAILED*\n" );
        return ERROR;
        }
    printf ("*OK*\n");
    
    CPUAffinitySet (1);
    taskPriorityGet (0, &prio);
    printf ("ATestSPRTP: call rtpSpawn... ");
    rtpId = rtpSpawn (TEST_RTP_NAME, pRtpArgs, NULL, 
                      prio - 1,   /* priority */ 
                      0x1000,   /* stack size */
                      0,
                      VX_FP_TASK);
    if (rtpId == RTP_ID_ERROR)
        {
        printf( "*FAILED*\n" );
        return ERROR;
        }
    printf ("OK, rtpid: %x\n", rtpId);
    
    printf ("ATestSPRTP: call timePartScheduleSet... ");
    if (timePartScheduleSet (schedId, TIME_PART_SCHED_CHANGE_NOW) != OK)
        {
        printf ("*FAILED*\n");   
        }
    printf ("*OK*\n");
    
    return OK;
    }


