FROM python:3.10

RUN mkdir -p /airbyte/integration_code/destination_sftp_csv
RUN mkdir -p /airbyte/integration_code/destination_azure_storage_csv

ADD ./pyproject.toml /airbyte/integration_code/

ADD ./README.md /airbyte/integration_code/

COPY ./destination_sftp_csv /airbyte/integration_code/destination_sftp_csv/
COPY ./destination_azure_storage_csv /airbyte/integration_code/destination_azure_storage_csv/

WORKDIR /airbyte/integration_code

ADD ./main.py /airbyte/integration_code/

RUN pip install .

ENTRYPOINT ["python3", "/airbyte/integration_code/main.py"]
