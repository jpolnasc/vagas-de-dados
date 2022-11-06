import pandas as pd
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def set_driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome("../driver/chromedriver", options=options)
    return driver

def go_to_website(website, driver):
    driver.get(website) 
    return None

def aceitar_coookies(driver):
    try:
        driver.find_element_by_xpath('//button[@id="onetrust-accept-btn-handler"]').click()
    except:
        pass
    return None

def pesquisar_qual_vaga(palavra_chave, driver):
    vaga = driver.find_element_by_name('q') 
    vaga.clear() 
    vaga.send_keys(palavra_chave)
    vaga.send_keys(Keys.RETURN)
    return None

def pesquisar_local_vaga(palavra_chave, driver):
    cargo_input = driver.find_element_by_name('l') 
    cargo_input.send_keys(Keys.COMMAND + "a")
    cargo_input.send_keys(Keys.DELETE)
    cargo_input.send_keys(palavra_chave)
    cargo_input.send_keys(Keys.RETURN)
    return None

def build_df_vagas(driver):
    
    lista_vagas = driver.find_elements_by_xpath('//div[@id="mosaic-provider-jobcards"]//ul[@class="jobsearch-ResultsList css-0"]//h2[@class = "jobTitle css-1h4a4n5 eu4oa1w0"]//a')
    
    D = []
    for vaga in lista_vagas:

        d = {
          "id": vaga.get_attribute("id"),
          "vaga": vaga.get_attribute("text"),
          "url": vaga.get_attribute("href")
        }
        D.append(d)
    df = pd.DataFrame.from_dict(D)
    return df

def go_to_next_page(driver):
    
    url = driver.find_elements_by_xpath('//a[@data-testid="pagination-page-next"]')[0].get_attribute('href')
    
    go_to_website(url, driver)
    
    return None

#----------------------------------------------------------------------------------------------------#

def get_titulo_vaga(driver):
    titulo = driver.find_elements_by_xpath('//div[@class="jobsearch-DesktopStickyContainer"]//h1')[0].text
    return titulo

def get_info_vaga(driver):
    info_vaga = driver.find_elements_by_xpath('//div[@class="jobsearch-DesktopStickyContainer"]//div[@class="jobsearch-CompanyInfoContainer"]')
    info_vaga = info_vaga[0].text.split("\n")
    info_vaga = ";".join(info_vaga)
    return info_vaga

def get_descricao_da_vaga(driver):
    desc = driver.find_elements_by_xpath('//div[@id="jobDescriptionText"]')[0].text.split("\n")
    desc = list(filter(None, desc))
    desc = ";".join(desc)
    return desc

def build_dic_info_vagas(url, driver):
    
    go_to_website(url, driver)
    
    d = {
      "titulo": get_titulo_vaga(driver),
      "info": get_info_vaga(driver),
      "descricao": get_descricao_da_vaga(driver)
    }

    return d

#----------------------------------------------------------------------------------------------------#

def get_df_vagas():

    DF = []

    driver = set_driver()
    go_to_website('https://br.indeed.com/', driver)
    aceitar_coookies(driver)
    pesquisar_qual_vaga("Cientista de Dados", driver)
    pesquisar_local_vaga("Brasil", driver)

    df = build_df_vagas(driver) #na primeira pagina

    for i in range(10): #primeiras 11 paginas

        try:

            go_to_next_page(driver)

            df = build_df_vagas(driver)

            DF.append(df)

        except:

            pass

        sleep(1)

    df_vagas = pd.concat(DF).reset_index(drop=True)
    return df_vagas


def get_df_info_vagas(df_vagas):

    driver = set_driver()

    urls = df_vagas.url.to_list()

    D = []
    for url in urls:
        d = build_dic_info_vagas(url, driver)
        D.append(d)
        sleep(1)
    
    df_infos = pd.DataFrame.from_dict(D)

    return df_infos


def main():

    df_vagas = get_df_vagas()
    df_infos = get_df_info_vagas(df_vagas)

    df_final = df_vagas.join(df_infos)

    df_final.to_csv("../data/vagas.csv")

main()