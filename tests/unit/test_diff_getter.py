"""
test_diff_getter.py
Date:  23/07/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com 
"""
from collections import namedtuple
from unittest.mock import patch

import pytest
import requests
from SPARQLWrapper import SPARQLWrapper

from rdf_differ.diff_getter import FusekiDiffGetter, FusekiException

RequestObj = namedtuple('RequestObj', ['status_code', 'url', 'text'])


def test_FusekiDiffGetter_sparql_endpoint():
    fuseki_service = FusekiDiffGetter(triplestore_service_url="http://localhost:3030")
    assert fuseki_service.make_sparql_endpoint(dataset_name="subdiv") == "http://localhost:3030/subdiv/sparql"
    assert fuseki_service.make_sparql_endpoint(dataset_name="/foe") == "http://localhost:3030/foe/sparql"

    fuseki_service = FusekiDiffGetter(triplestore_service_url="http://localhost:3030/")
    assert fuseki_service.make_sparql_endpoint(dataset_name="subdiv") == "http://localhost:3030/subdiv/sparql"
    assert fuseki_service.make_sparql_endpoint(dataset_name="/foe") == "http://localhost:3030/foe/sparql"


@patch.object(requests, 'get')
def test_FusekiDiffGetter_list_datasets(mock_get):
    response_text = """{ 
          "datasets" : [ 
              { 
                "ds.name" : "/subdiv" ,
                "ds.state" : true ,
                "ds.services" : [ 
                    { 
                      "srv.type" : "gsp-rw" ,
                      "srv.description" : "Graph Store Protocol" ,
                      "srv.endpoints" : [ "data" ]
                    } ,
                    { 
                      "srv.type" : "query" ,
                      "srv.description" : "SPARQL Query" ,
                      "srv.endpoints" : [ 
                          "" ,
                          "sparql" ,
                          "query"
                        ]
                    } ,
                    { 
                      "srv.type" : "gsp-r" ,
                      "srv.description" : "Graph Store Protocol (Read)" ,
                      "srv.endpoints" : [ "get" ]
                    } ,
                    { 
                      "srv.type" : "update" ,
                      "srv.description" : "SPARQL Update" ,
                      "srv.endpoints" : [ 
                          "update" ,
                          ""
                        ]
                    } ,
                    { 
                      "srv.type" : "upload" ,
                      "srv.description" : "File Upload" ,
                      "srv.endpoints" : [ "upload" ]
                    }
                  ]
              } ,
              { 
                "ds.name" : "/qwe" ,
                "ds.state" : true ,
                "ds.services" : [ 
                    { 
                      "srv.type" : "gsp-rw" ,
                      "srv.description" : "Graph Store Protocol" ,
                      "srv.endpoints" : [ "data" ]
                    } ,
                    { 
                      "srv.type" : "query" ,
                      "srv.description" : "SPARQL Query" ,
                      "srv.endpoints" : [ 
                          "query" ,
                          "sparql" ,
                          ""
                        ]
                    } ,
                    { 
                      "srv.type" : "gsp-r" ,
                      "srv.description" : "Graph Store Protocol (Read)" ,
                      "srv.endpoints" : [ "get" ]
                    } ,
                    { 
                      "srv.type" : "update" ,
                      "srv.description" : "SPARQL Update" ,
                      "srv.endpoints" : [ 
                          "" ,
                          "update"
                        ]
                    } ,
                    { 
                      "srv.type" : "upload" ,
                      "srv.description" : "File Upload" ,
                      "srv.endpoints" : [ "upload" ]
                    }
                  ]
              } ,
              { 
                "ds.name" : "/rty" ,
                "ds.state" : true ,
                "ds.services" : [ 
                    { 
                      "srv.type" : "gsp-rw" ,
                      "srv.description" : "Graph Store Protocol" ,
                      "srv.endpoints" : [ "data" ]
                    } ,
                    { 
                      "srv.type" : "query" ,
                      "srv.description" : "SPARQL Query" ,
                      "srv.endpoints" : [ 
                          "query" ,
                          "" ,
                          "sparql"
                        ]
                    } ,
                    { 
                      "srv.type" : "gsp-r" ,
                      "srv.description" : "Graph Store Protocol (Read)" ,
                      "srv.endpoints" : [ "get" ]
                    } ,
                    { 
                      "srv.type" : "update" ,
                      "srv.description" : "SPARQL Update" ,
                      "srv.endpoints" : [ 
                          "" ,
                          "update"
                        ]
                    } ,
                    { 
                      "srv.type" : "upload" ,
                      "srv.description" : "File Upload" ,
                      "srv.endpoints" : [ "upload" ]
                    }
                  ]
              }
            ]
        }
        """

    mock_get.return_value = RequestObj(200, 'http://some.url', response_text)
    fuseki_service = FusekiDiffGetter(triplestore_service_url="http://localhost:3030/")

    assert 3 == len(fuseki_service.list_datasets())
    assert '/subdiv' in fuseki_service.list_datasets()


@patch.object(requests, 'get')
def test_FusekiDiffGetter_list_datasets_failing(mock_get):
    mock_get.return_value = RequestObj(400, 'http://some.url', None)
    fuseki_service = FusekiDiffGetter(triplestore_service_url="http://localhost:3030/")

    with pytest.raises(FusekiException) as exception:
        fuseki_service.list_datasets()

    assert '400' in str(exception.value)


@patch.object(SPARQLWrapper, 'query')
def test_FusekiDiffGetter_dataset_description(mock_query):
    def convert():
        return {
            "head": {
                "vars": ["versionHistoryGraph", "datasetVersion", "date", "currentVersionGraph", "schemeURI",
                         "versionNamedGraph", "versionId"]
            },
            "results": {
                "bindings": [
                    {
                        "versionHistoryGraph": {"type": "uri",
                                                "value": "http://publications.europa.eu/resource/authority/subdivision/version"},
                        "datasetVersion": {"type": "literal", "value": "20171213-0"},
                        "schemeURI": {"type": "uri",
                                      "value": "http://publications.europa.eu/resource/authority/subdivision"},
                        "versionNamedGraph": {"type": "uri",
                                              "value": "http://publications.europa.eu/resource/authority/subdivision/version/v1"},
                        "versionId": {"type": "literal", "value": "v1"}
                    },
                    {
                        "versionHistoryGraph": {"type": "uri",
                                                "value": "http://publications.europa.eu/resource/authority/subdivision/version"},
                        "datasetVersion": {"type": "literal", "value": "20190220-0"},
                        "currentVersionGraph": {"type": "uri",
                                                "value": "http://publications.europa.eu/resource/authority/subdivision/version/v2"},
                        "schemeURI": {"type": "uri",
                                      "value": "http://publications.europa.eu/resource/authority/subdivision"},
                        "versionNamedGraph": {"type": "uri",
                                              "value": "http://publications.europa.eu/resource/authority/subdivision/version/v2"},
                        "versionId": {"type": "literal", "value": "v2"}
                    }
                ]
            }
        }

    mock_query.return_value = mock_query
    mock_query.convert = convert

    fuseki_service = FusekiDiffGetter(triplestore_service_url="http://localhost:3030/")
    response = fuseki_service.diff_description(dataset_name='/subdiv')

    assert response['versionHistoryGraph'] == "http://publications.europa.eu/resource/authority/subdivision/version"
    assert response['currentVersionGraph'] == "http://publications.europa.eu/resource/authority/subdivision/version/v2"
    assert response['datasetURI'] == "http://publications.europa.eu/resource/authority/subdivision"

    assert "20171213-0" in response['datasetVersions'] and "20190220-0" in response['datasetVersions']
    assert "v1" in response['versionIds'] and "v2" in response['versionIds']
    assert "http://publications.europa.eu/resource/authority/subdivision/version/v1" in response['versionNamedGraphs'] \
           and "http://publications.europa.eu/resource/authority/subdivision/version/v2" in response[
               'versionNamedGraphs']


@patch.object(SPARQLWrapper, 'query')
def test_FusekiDiffGetter_diff_description_failing(mock_query):
    def convert():
        return {'head': {'vars': ['datasetURI', 'versionDescriptionGraph']}, 'results': {'bindings': []}}

    mock_query.return_value = mock_query
    mock_query.convert = convert

    fuseki_service = FusekiDiffGetter(triplestore_service_url="http://localhost:3030/")

    with pytest.raises(IndexError):
        fuseki_service.diff_description(dataset_name='/subdiv')


@patch.object(SPARQLWrapper, 'query')
def test_FusekiDiffGetter_diff_description_failing1(mock_query):
    def convert():
        return {}

    mock_query.return_value = mock_query
    mock_query.convert = convert

    fuseki_service = FusekiDiffGetter(triplestore_service_url="http://localhost:3030/")

    with pytest.raises(KeyError):
        fuseki_service.diff_description(dataset_name='/subdiv')


@patch.object(SPARQLWrapper, 'query')
def test_FusekiDiffGetter_count_inserted_triples_success(mock_query):
    def convert():
        return {
            "head": {
                "vars": ["insertionsGraph", "triplesInInsertionGraph"]
            },
            "results": {
                "bindings": [
                    {
                        "insertionsGraph": {"type": "uri",
                                            "value": "http://publications.europa.eu/resource/authority/subdivision/version/v1/delta/v2/insertions"},
                        "triplesInInsertionGraph": {"type": "literal",
                                                    "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                                                    "value": "387"}
                    }
                ]
            }
        }

    # this is a hack, for mocking the SPARQL result set as well, along with the SPARQLWrapper
    mock_query.return_value = mock_query
    mock_query.convert = convert

    fuseki_service = FusekiDiffGetter(triplestore_service_url="http://localhost:3030/")
    count = fuseki_service.count_inserted_triples('subdiv')

    assert 387 == count


@patch.object(SPARQLWrapper, 'query')
def test_FusekiDiffGetter_count_inserted_triples_failing(mock_query):
    def convert():
        return {
            "head": {
                "vars": ["insertionsGraph", "triplesInInsertionGraph"]
            },
            "results": {
                "bindings": []
            }
        }

    # this is a hack, for mocking the SPARQL result set as well, along with the SPARQLWrapper
    mock_query.return_value = mock_query
    mock_query.convert = convert

    fuseki_service = FusekiDiffGetter(triplestore_service_url="http://localhost:3030/")

    with pytest.raises(IndexError):
        fuseki_service.count_inserted_triples('subdiv')


@patch.object(SPARQLWrapper, 'query')
def test_FusekiDiffGetter_count_deleted_triples_success(mock_query):
    def convert():
        return {
            "head": {
                "vars": ["deletionsGraph", "triplesInDeletionGraph", "versionGraph"]
            },
            "results": {
                "bindings": [
                    {
                        "deletionsGraph": {"type": "uri",
                                           "value": "http://publications.europa.eu/resource/authority/subdivision/version/v1/delta/v2/deletions"},
                        "triplesInDeletionGraph": {"type": "literal",
                                                   "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                                                   "value": "3"},
                        "versionGraph": {"type": "uri",
                                         "value": "http://publications.europa.eu/resource/authority/subdivision/version"}
                    }
                ]
            }
        }

    # this is a hack, for mocking the SPARQL result set as well, along with the SPARQLWrapper
    mock_query.return_value = mock_query
    mock_query.convert = convert

    fuseki_service = FusekiDiffGetter(triplestore_service_url="http://localhost:3030/")
    count = fuseki_service.count_deleted_triples('subdiv')

    assert 3 == count

