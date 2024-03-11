import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import tabula
import numpy.typing as npt

URL = ("https://cdn.who.int/media/docs/default-source/gho-documents/global-health-estimates/"
       "gpe_discussion_paper_series_paper31_2001_age_standardization_rates.pdf")


def read_who_std_pop(url: str = URL) -> npt.NDArray[float]:
    """Reads the WHO standard population distribution from the PDF file provided.

    Parameters
    ----------
    :param url: URL of the PDF file
    :type url: str
    :return: WHO standard population proportions
    :rtype: np.ndarray
    """
    # Download WHO Standard Population PDF
    file = open("data/who_std_pop.pdf", "wb")
    url_request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    webpage = urlopen(url_request).read()
    file.write(webpage)
    file.close()

    # Read column "WHO World Standard*" in Table 1 on page 10
    tables = tabula.read_pdf("data/who_std_pop.pdf", pages=10)  # two tables on page 10
    table1 = tables[0]['Table 1. Standard Population Distribution (percent)'].values

    who_std_pop = np.array([row.split(" ")[-1] for row in table1[1:-3]], dtype=np.float32)  # convert to numeric
    return who_std_pop / who_std_pop.sum()  # requires proportions, not percentages


def read_table_from_notion() -> pd.DataFrame:
    """Reads the table from the HTML file provided by OWID and returns.

    Parameters
    ----------
    :return: Death rates by age group for the USA and Uganda
    :rtype: pd.DataFrame
    """
    # Read HML page
    with open("data/owid_notion_page.html", "r", encoding="utf-8") as file:
        notion_page_html = file.read()

    # Notion uses the class 'notion-table'
    soup = BeautifulSoup(notion_page_html, 'html.parser')
    rows = soup.find_all('tr', class_='notion-table-row')

    # Parse data, ignoring white space
    data = []
    for row in rows[1:]:  # avoid headings
        cells = row.find_all('div', class_='notion-table-cell-text')
        row_data = [cell.get_text(strip=True) for cell in cells]
        data.append(row_data)

    df = pd.DataFrame(data, columns=['age', 'usa', 'uganda'])
    df['usa'] = pd.to_numeric(df['usa'])
    df['uganda'] = pd.to_numeric(df['uganda'])
    return df


def population_proportions(data: pd.DataFrame, country: str) -> npt.NDArray[float]:
    """Computes population proportions for a given country and year.

    Parameters
    ----------
    :param data: Data frame containing UN population data
    :type data: pd.DataFrame
    :param country: Country for which to compute population proportions
    :type country: str
    :return: Population proportions for the given country
    :rtype: np.ndarray
    """
    # could use @country but Pylint complaints unnecessarily
    filtered_data = data.query("Location == '{}' and Year == 2019".format(country))['PopTotal']
    summary = np.append(filtered_data.values[:17], filtered_data.values[17:].sum())
    return summary / summary.sum()


def read_UN_population_data() -> tuple[npt.NDArray[float], npt.NDArray[float]]:
    """Reads UN Population data for the USA and Uganda and computes the population proportions for the year 2019.

    Parameters
    ----------
    :return: Population proportions for the USA and Uganda
    :rtype: tuple[np.ndarray, np.ndarray]
    """
    columns = ['Location', 'Time', 'AgeGrp', 'PopTotal']
    UN_data = pd.read_csv("data/WPP2022_PopulationByAge5GroupSex_Medium.csv", usecols=columns)
    UN_data = UN_data[UN_data['Location'].isin(['Uganda', 'United States of America'])]
    UN_data = UN_data.rename(columns={"Time": "Year"})
    # Compute proportions for the USA and Uganda
    usa_pop_props = population_proportions(UN_data, "United States of America")
    uganda_pop_props = population_proportions(UN_data, "Uganda")
    return usa_pop_props, uganda_pop_props
