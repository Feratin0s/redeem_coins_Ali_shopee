#../logs --> Pasta pra salvar os erros e imagens

def debug(d):
    d.screenshot("bug.png")
    xml = d.dump_hierarchy()
    print(xml)