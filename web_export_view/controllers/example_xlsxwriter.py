if __name__ == '__main__':
    import xlsxwriter
    workbook2 = xlsxwriter.Workbook('C:\Users\Sistemas\Downloads\cer.xlsx')
    worksheet = workbook2.add_worksheet('mio')
    worksheet.write('A1', 'Operadora')
    worksheet.write('A2', 'pae')
    worksheet.write('A3', 'ypf')
    worksheet.write('A4', 'aeswdrfa')
    worksheet.write('A5', 'dsfds')
    worksheet.autofilter(0, 0, 4,0)
    worksheet.set_column(0, 0, 16)
    workbook2.close()
    print 'aaa'