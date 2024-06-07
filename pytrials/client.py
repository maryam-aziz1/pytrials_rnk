from pytrials.utils import json_handler, csv_handler
from pytrials import study_fields
import csv


class ClinicalTrials:
    """ClinicalTrials API client

    Provides functions to easily access the ClinicalTrials.gov API
    (https://classic.clinicaltrials.gov/api/)
    in Python.

    Attributes:
        study_fields: List of all study fields you can use in your query.
        api_info: Tuple containing the API version number and the last
        time the database was updated.
    """

    _BASE_URL = "https://clinicaltrials.gov/api/v2/"
    _JSON = "format=json"
    _CSV = "format=csv"

    def __init__(self):
        self.api_info = self.__api_info()

    @property
    def study_fields(self):
        """List of all study fields you can use in your query."""

        csv_fields = []
        json_fields = []
        with open(study_fields, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                csv_fields.append(row["Column Name"])
                json_fields.append(row["Included Data Fields"].split("|"))

        return {
            "csv": csv_fields,
            "json": [item for sublist in json_fields for item in sublist],
        }

    def __api_info(self):
        """Returns information about the API"""
        req = json_handler(f"{self._BASE_URL}version")
        last_updated = req["dataTimestamp"]

        api_version = req["apiVersion"]

        return api_version, last_updated

    def get_full_studies(self, search_expr, max_studies=50, fmt="csv"):
        """Returns all content for a maximum of 100 study records.

        Retrieves information from the full studies endpoint, which gets all study fields.
        This endpoint can only output JSON (Or not-supported XML) format and does not allow
        requests for more than 100 studies at once.

        Args:
            search_expr (str): A string containing a search expression as specified by
                `their documentation <https://clinicaltrials.gov/api/gui/ref/syntax#searchExpr>`_.
            max_studies (int): An integer indicating the maximum number of studies to return.
                Defaults to 50.

        Returns:
            dict: Object containing the information queried with the search expression.

        Raises:
            ValueError: The number of studies can only be between 1 and 100
        """
        if fmt == "csv":
            format = self._CSV
            handler = csv_handler
        elif fmt == "json":
            format = self._JSON
            handler = json_handler
        else:
            raise ValueError("Format argument has to be either 'csv' or 'json")

        if max_studies > 1000 or max_studies < 1:
            raise ValueError("The number of studies can only be between 1 and 1000")

        req = f"studies?{format}&markupFormat=legacy&query.term={search_expr}&pageSize={max_studies}"

        full_studies = handler(f"{self._BASE_URL}{req}")

        return full_studies

def get_study_fields(
    self, search_expr, fields, max_studies=50, min_rnk=1, fmt="csv"
):
    """Returns study content for specified fields

    Retrieves information from the study fields endpoint, which acquires specified information
    from a large number of studies. To see a list of all possible fields, check the class'
    study_fields attribute.

    Args:
        search_expr (str): A string containing a search expression.
        fields (list(str)): A list containing the desired information fields.
        max_studies (int): An integer indicating the maximum number of studies to return.
        min_rnk (int): Minimum Rank sets the lower limit on the range of study records to return.
        fmt (str): The output format, either 'csv' or 'json'.

    Returns:
        Either a dict, if fmt='json', or a list of records (e.g., a list of lists), if fmt='csv'.
        Both containing the maximum number of study fields queried with the specified search expression.

    Raises:
        ValueError: The number of studies or minimum rank are out of valid range.
        ValueError: One of the fields is not valid.
    """
    if fmt not in ['csv', 'json']:
        raise ValueError("Format argument has to be either 'csv' or 'json'")
    if max_studies > 1000 or max_studies < 1:
        raise ValueError("The number of studies can only be between 1 and 1000")
    if min_rnk < 1:
        raise ValueError("Minimum rank (min_rnk) must be at least 1")
    if not set(fields).issubset(self.study_fields[fmt]):
        raise ValueError("One of the fields is not valid! Check the study_fields attribute for a list of valid ones.")

    concat_fields = "|".join(fields)
    req = f"&query.term={search_expr}&markupFormat=legacy&fields={concat_fields}&min_rnk={min_rnk}&pageSize={max_studies}"
    url = f"{self._BASE_URL}studies?{self._CSV if fmt == 'csv' else self._JSON}{req}"
    return csv_handler(url) if fmt == 'csv' else json_handler(url)

    def __repr__(self):
        return f"ClinicalTrials.gov client v{self.api_info[0]}, database last updated {self.api_info[1]}"
