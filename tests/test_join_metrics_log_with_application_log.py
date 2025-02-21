import unittest
import tempfile
import os
import sys
from io import StringIO
import contextlib

import json
from join_metrics_log_with_application_log import join_olfs_metrics_log_with_bes_application_log_entries

verbose = True

metrics_log =   [
    {
        "request_id": "https-openssl-apr-8443-exec-7_37_4b6c1400-d790-481f-987e-202bfcd74b58",
        "user_id": "dongwu",
        "user_ip": "10.11.255.129",
        "rangeBeginDateTime": "",
        "rangeEndDateTime": "",
        "collectionId": "/hyrax/ngap/collections/C2938661904-NSIDC_CPRD/granules/SMAP_L1B_TB_49749_A_20240525T040723_R19240_001.h5.dmr.html",
        "parameters": {
          "service_name": "hyrax",
          "service_provider": "OPeNDAP",
          "service_id": "hyrax_prod"
        },
        "job_ids": [
          "N/A"
        ],
        "http_response_code": 404,
        "time_completed": "2025-02-14T07:00:12+0000",
        "total_time": 2631,
        "output_size": -1
    }
]

application_log = [
    {
        "hyrax-bes-action": "get.dmr",
        "hyrax-ce": "-",
        "hyrax-client-ip": "10.11.255.129",
        "hyrax-http-verb": "HTTP-GET",
        "hyrax-instance-id": "h-8bfd6a17-a17e-460a-b0d2-1fe8cefaafdd",
        "hyrax-local-path": "collections/C2938661904-NSIDC_CPRD/granules/SMAP_L1B_TB_49749_A_20240525T040723_R19240_001.h5",
        "hyrax-olfs-start-time": 1739516409753,
        "hyrax-pid": 29751,
        "hyrax-query-string": "-",
        "hyrax-request-id": "https-openssl-apr-8443-exec-7_37_4b6c1400-d790-481f-987e-202bfcd74b58",
        "hyrax-return-as": "dap",
        "hyrax-session-id": "8A69DB9E21B5471C6DD61B5BD6D80F45",
        "hyrax-time": 1739516409,
        "hyrax-type": "request",
        "hyrax-url-path": "/hyrax/ngap/collections/C2938661904-NSIDC_CPRD/granules/SMAP_L1B_TB_49749_A_20240525T040723_R19240_001.h5.dmr.html",
        "hyrax-user-agent": "Wget#1#19#5 #linux-gnu#",
        "hyrax-user-id": "dongwu"
    },
    {
        "hyrax-instance-id": "h-8bfd6a17-a17e-460a-b0d2-1fe8cefaafdd",
        "hyrax-message": "NgapOwnedContainer::get_item_from_dmrpp_cache() - Memory Cache miss, DMR++: collections/C2938661904-NSIDC_CPRD/granules/SMAP_L1B_TB_49749_A_20240525T040723_R19240_001.h5",
        "hyrax-pid": 29751,
        "hyrax-time": 1739516409,
        "hyrax-type": "info"
    },
    {
        "hyrax-instance-id": "h-8bfd6a17-a17e-460a-b0d2-1fe8cefaafdd",
        "hyrax-message": "NgapOwnedContainer::get_item_from_dmrpp_cache() - File Cache miss, DMR++: collections/C2938661904-NSIDC_CPRD/granules/SMAP_L1B_TB_49749_A_20240525T040723_R19240_001.h5",
        "hyrax-pid": 29751,
        "hyrax-time": 1739516409,
        "hyrax-type": "info"
    },
    {
        "hyrax-instance-id": "h-8bfd6a17-a17e-460a-b0d2-1fe8cefaafdd",
        "hyrax-message": "NgapOwnedContainer::build_data_url_to_daac_bucket() - CMR Cache miss, REST path: collections/C2938661904-NSIDC_CPRD/granules/SMAP_L1B_TB_49749_A_20240525T040723_R19240_001.h5:dongwu",
        "hyrax-pid": 29751,
        "hyrax-time": 1739516409,
        "hyrax-type": "info"
    },
    {
        "hyrax-instance-id": "h-8bfd6a17-a17e-460a-b0d2-1fe8cefaafdd",
        "hyrax-message": "NgapOwnedContainer::build_data_url_to_daac_bucket() - CMR Cache put, translated URL: https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/SMAP/SPL1BTB/006/2024/05/25/SMAP_L1B_TB_49749_A_20240525T040723_R19240_001.h5",
        "hyrax-pid": 29751,
        "hyrax-time": 1739516410,
        "hyrax-type": "info"
    },
    {
        "hyrax-instance-id": "h-8bfd6a17-a17e-460a-b0d2-1fe8cefaafdd",
        "hyrax-message": "NgapOwnedContainer::dmrpp_read_from_daac_bucket() - Look in the DAAC-bucket for the DMRpp for: https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/SMAP/SPL1BTB/006/2024/05/25/SMAP_L1B_TB_49749_A_20240525T040723_R19240_001.h5.dmrpp",
        "hyrax-pid": 29751,
        "hyrax-time": 1739516410,
        "hyrax-type": "info"
    },
    {
        "hyrax-instance-id": "h-8bfd6a17-a17e-460a-b0d2-1fe8cefaafdd",
        "hyrax-message": "ERROR! HttpError: ERROR - The HTTP GET request for the source URL: https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/SMAP/SPL1BTB/006/2024/05/25/SMAP_L1B_TB_49749_A_20240525T040723_R19240_001.h5.dmrpp FAILED. CURLINFO_EFFECTIVE_URL: https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/SMAP/SPL1BTB/006/2024/05/25/SMAP_L1B_TB_49749_A_20240525T040723_R19240_001.h5.dmrpp The response from https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/SMAP/SPL1BTB/006/2024/05/25/SMAP_L1B_TB_49749_A_20240525T040723_R19240_001.h5.dmrpp (Originally: https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/SMAP/SPL1BTB/006/2024/05/25/SMAP_L1B_TB_49749_A_20240525T040723_R19240_001.h5.dmrpp) returned an HTTP code of 404 which means Not Found: The underlying data source or server could not be found. NgapOwnedContainer::dmrpp_read_from_daac_bucket() failed to read the DMR++ from S3. (CurlUtils.cc:798) Current memory usage is: 186408 KB.",
        "hyrax-pid": 29751,
        "hyrax-time": 1739516412,
        "hyrax-type": "error"
    },
    {
        "hyrax-instance-id": "h-8bfd6a17-a17e-460a-b0d2-1fe8cefaafdd",
        "hyrax-message": "This error should not be merged - outside time boundary",
        "hyrax-pid": 29751,
        "hyrax-time": 1739516485,
        "hyrax-type": "error"
    }

]

expected_output =   [
    {
        "request_id": "https-openssl-apr-8443-exec-7_37_4b6c1400-d790-481f-987e-202bfcd74b58",
        "user_id": "dongwu",
        "user_ip": "10.11.255.129",
        "rangeBeginDateTime": "",
        "rangeEndDateTime": "",
        "collectionId": "/hyrax/ngap/collections/C2938661904-NSIDC_CPRD/granules/SMAP_L1B_TB_49749_A_20240525T040723_R19240_001.h5.dmr.html",
        "parameters": {
            "service_name": "hyrax",
            "service_provider": "OPeNDAP",
            "service_id": "hyrax_prod"
        },
        "job_ids": [
            "N/A"
        ],
        "http_response_code": 404,
        "time_completed": "2025-02-14T07:00:12+0000",
        "total_time": 2631,
        "output_size": -1,
        "bes": {
            "request": {
                "hyrax-bes-action": "get.dmr",
                "hyrax-ce": "-",
                "hyrax-client-ip": "10.11.255.129",
                "hyrax-http-verb": "HTTP-GET",
                "hyrax-instance-id": "h-8bfd6a17-a17e-460a-b0d2-1fe8cefaafdd",
                "hyrax-local-path": "collections/C2938661904-NSIDC_CPRD/granules/SMAP_L1B_TB_49749_A_20240525T040723_R19240_001.h5",
                "hyrax-olfs-start-time": 1739516409753,
                "hyrax-pid": 29751,
                "hyrax-query-string": "-",
                "hyrax-request-id": "https-openssl-apr-8443-exec-7_37_4b6c1400-d790-481f-987e-202bfcd74b58",
                "hyrax-return-as": "dap",
                "hyrax-session-id": "8A69DB9E21B5471C6DD61B5BD6D80F45",
                "hyrax-time": 1739516409,
                "hyrax-type": "request",
                "hyrax-url-path": "/hyrax/ngap/collections/C2938661904-NSIDC_CPRD/granules/SMAP_L1B_TB_49749_A_20240525T040723_R19240_001.h5.dmr.html",
                "hyrax-user-agent": "Wget#1#19#5 #linux-gnu#",
                "hyrax-user-id": "dongwu"
            },
            "related_entries": [
                {
                    "hyrax-instance-id": "h-8bfd6a17-a17e-460a-b0d2-1fe8cefaafdd",
                    "hyrax-message": "NgapOwnedContainer::get_item_from_dmrpp_cache() - Memory Cache miss, DMR++: collections/C2938661904-NSIDC_CPRD/granules/SMAP_L1B_TB_49749_A_20240525T040723_R19240_001.h5",
                    "hyrax-pid": 29751,
                    "hyrax-time": 1739516409,
                    "hyrax-type": "info"
                },
                {
                    "hyrax-instance-id": "h-8bfd6a17-a17e-460a-b0d2-1fe8cefaafdd",
                    "hyrax-message": "NgapOwnedContainer::get_item_from_dmrpp_cache() - File Cache miss, DMR++: collections/C2938661904-NSIDC_CPRD/granules/SMAP_L1B_TB_49749_A_20240525T040723_R19240_001.h5",
                    "hyrax-pid": 29751,
                    "hyrax-time": 1739516409,
                    "hyrax-type": "info"
                },
                {
                    "hyrax-instance-id": "h-8bfd6a17-a17e-460a-b0d2-1fe8cefaafdd",
                    "hyrax-message": "NgapOwnedContainer::build_data_url_to_daac_bucket() - CMR Cache miss, REST path: collections/C2938661904-NSIDC_CPRD/granules/SMAP_L1B_TB_49749_A_20240525T040723_R19240_001.h5:dongwu",
                    "hyrax-pid": 29751,
                    "hyrax-time": 1739516409,
                    "hyrax-type": "info"
                },
                {
                    "hyrax-instance-id": "h-8bfd6a17-a17e-460a-b0d2-1fe8cefaafdd",
                    "hyrax-message": "NgapOwnedContainer::build_data_url_to_daac_bucket() - CMR Cache put, translated URL: https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/SMAP/SPL1BTB/006/2024/05/25/SMAP_L1B_TB_49749_A_20240525T040723_R19240_001.h5",
                    "hyrax-pid": 29751,
                    "hyrax-time": 1739516410,
                    "hyrax-type": "info"
                },
                {
                    "hyrax-instance-id": "h-8bfd6a17-a17e-460a-b0d2-1fe8cefaafdd",
                    "hyrax-message": "NgapOwnedContainer::dmrpp_read_from_daac_bucket() - Look in the DAAC-bucket for the DMRpp for: https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/SMAP/SPL1BTB/006/2024/05/25/SMAP_L1B_TB_49749_A_20240525T040723_R19240_001.h5.dmrpp",
                    "hyrax-pid": 29751,
                    "hyrax-time": 1739516410,
                    "hyrax-type": "info"
                },
                {
                    "hyrax-instance-id": "h-8bfd6a17-a17e-460a-b0d2-1fe8cefaafdd",
                    "hyrax-message": "ERROR! HttpError: ERROR - The HTTP GET request for the source URL: https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/SMAP/SPL1BTB/006/2024/05/25/SMAP_L1B_TB_49749_A_20240525T040723_R19240_001.h5.dmrpp FAILED. CURLINFO_EFFECTIVE_URL: https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/SMAP/SPL1BTB/006/2024/05/25/SMAP_L1B_TB_49749_A_20240525T040723_R19240_001.h5.dmrpp The response from https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/SMAP/SPL1BTB/006/2024/05/25/SMAP_L1B_TB_49749_A_20240525T040723_R19240_001.h5.dmrpp (Originally: https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/SMAP/SPL1BTB/006/2024/05/25/SMAP_L1B_TB_49749_A_20240525T040723_R19240_001.h5.dmrpp) returned an HTTP code of 404 which means Not Found: The underlying data source or server could not be found. NgapOwnedContainer::dmrpp_read_from_daac_bucket() failed to read the DMR++ from S3. (CurlUtils.cc:798) Current memory usage is: 186408 KB.",
                    "hyrax-pid": 29751,
                    "hyrax-time": 1739516412,
                    "hyrax-type": "error"
                }
            ]
        }
    }
]




def loggy(message: str):
    """
    Prints a log message tpo stderr when verbose is enabled.
    """
    if verbose:
        print(f"# {message}", file=sys.stderr)


class TestJoinJsonArrays(unittest.TestCase):

    def setUp(self):
        # Create temporary files for left, right, and result.
        self.metrics_log_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        self.application_log_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        self.result_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)

    def tearDown(self):
        # Close and remove temporary files.
        self.metrics_log_file.close()
        self.application_log_file.close()
        self.result_file.close()
        os.remove(self.metrics_log_file.name)
        os.remove(self.application_log_file.name)
        os.remove(self.result_file.name)

    def test_join_olfs_metrics_log_with_bes_application_log_entries(self):

        json.dump(metrics_log, self.metrics_log_file)
        self.metrics_log_file.seek(0)
        json.dump(application_log, self.application_log_file)
        self.application_log_file.seek(0)

        # Call the function

        join_olfs_metrics_log_with_bes_application_log_entries(self.metrics_log_file.name, self.application_log_file.name, self.result_file.name)
        loggy(f"self.result_file.name: {self.result_file.name}")

        # Verify that the output file contains the expected joined records.
        with open(self.result_file.name, 'r') as f:
            joined_data = json.load(f)
        self.assertEqual(joined_data, expected_output)


if __name__ == '__main__':
    unittest.main()
