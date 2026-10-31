def redeem(d):
    d.app_start("com.alibaba.aliexpresshd") #Aliexpress
    #d.app_start("com.shopee.br") #Shopee
    xml = d.dump_hierarchy()
    #print(d.app_current())
    #print(xml)

    d(text="Moedas").click()
    