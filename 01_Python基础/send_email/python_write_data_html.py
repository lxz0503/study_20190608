
# TODO,read data from other files like csv,excel,json or mysql

tcp_64_name = 'tcp_64'
tcp_64_data = 90

with open('xiaozhan.html', 'w') as f:
    row1 = """<table border="1" class="dataframe"><tr style="text-align: right;">
      <th>{0}</th>
      <th>{1}</th>
    </tr>""".format(tcp_64_name, tcp_64_data)

    row2 = """<tr>
      <td>{0}</td>
      <td>{1}</td>
    </tr>""".format('tcp_1024', '1000')

    row3 = """<tr>
      <td>{0}</td>
      <td>{1}</td>
    </tr>""".format('tcp_65536', '955')

    row4 = """<tr>
      <td>{0}</td>
      <td>{1}</td>
       </tr>
      </tbody>
      </table>""".format('udp_1400', '938')

    f.write(row1+row2+row3+row4)

