# -*- coding: utf-8 -*-
from django.core.files.uploadhandler import TemporaryFileUploadHandler, \
                                                StopUpload


class QuotaUploadHandler(TemporaryFileUploadHandler):
    """
    This test upload handler terminates the connection if more than a quota
    (6MB) is uploaded.
    """

    QUOTA = 6 * 2 ** 20  # 6 MB

    def __init__(self, request=None):
        super(QuotaUploadHandler, self).__init__(request)
        self.total_upload = 0

    def receive_data_chunk(self, raw_data, start):
        self.total_upload += len(raw_data)
        if self.total_upload >= self.QUOTA:
            raise StopUpload(connection_reset=True)
        else:
            self.file.write(raw_data)
