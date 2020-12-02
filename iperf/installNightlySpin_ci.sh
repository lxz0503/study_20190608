#!/bin/bash

nightlyScriptDir=/buildarea1/hyan1/nightly
export PATH=$PATH:$nightlyScriptDir

rm $nightlyScriptDir/spinReady


#copy SPIN name conf file
remoteSpinConfFile=/net/pek-vx-nightly1/buildarea1/pzhang1/jenkinsEnvInjection/vx7_ci_nightly_spin.config
#remoteSpinConfFile=/buildarea1/hyan1/vx7_nightly_spin.config
spinConfFile=$nightlyScriptDir/vx7_nightly_spin.config
cp $remoteSpinConfFile $spinConfFile 
if [ $? != 0 ]; then
    echo -e "Copy SPIN name conf file $remoteSpinConfFile to $spinConfFile failed"
fi

#check whether NIGHTLYSPIN has value, if yes, install the nightly test spin, if no, exit

spin=$(cat $spinConfFile| grep 'NIGHTLYSPIN' | awk -F= '{print $2}')
if [ -z $spin ]; then
    echo -e "There is not new spin for nightly test"
    exit 0
fi

spinPath=/buildarea1/hyan1/nightly/$spin;

echo -E "spin=$spin"
echo -E "spinPath=$spinPath"


# cd /net/pek-cdftp/pek-cdftp1/ftp/r1/vxworks/vxworks-7.0/$spin/bootstrap_installer/
cd /net/pek-cdftp/pek-cdftp1/ftp/r1/vxworks/vxworks-7-r2/$spin/bootstrap_installer/
./setup_linux -productUpdateURLS none -silent -installPath $spinPath

cd $spinPath
#cp /folk/hyan1/zwrsLicense.lic license/
cp /net/pek-cdftp/pek-cdftp1/ftp/r1/license/WRSLicense.lic license/
chmod 777 -R $spinPath

# install ipert
cd vxworks-7/pkgs_v2/net
mkdir app
cp -r /folk/hyan1/iperf3 app
chmod -R 777 app



flagFile=$nightlyScriptDir/spinReady
echo -e "flagFile=$flagFile"
echo $spin > $flagFile

echo -e "Nightly test spin install successfully"
exit 0
