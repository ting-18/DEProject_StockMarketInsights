# First-time build can take upto 10 mins.

#Pick a image:https://hub.docker.com/r/apache/airflow/tags?name=3.8
FROM apache/airflow:2.10.5-python3.8

ENV AIRFLOW_HOME=/opt/airflow
#for dbt:tells dbt where to find the profiles.yml configuration file,
# which contains database connection settings.
ENV DBT_PROFILES_DIR=/opt/airflow/.dbt

USER root
RUN apt-get update -qq && apt-get install vim -qqq
# git gcc g++ -qqq

# Ref: https://airflow.apache.org/docs/docker-stack/recipes.html
SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

ARG CLOUD_SDK_VERSION=322.0.0
ENV GCLOUD_HOME=/home/google-cloud-sdk
ENV PATH="${GCLOUD_HOME}/bin/:${PATH}"


RUN DOWNLOAD_URL="https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-${CLOUD_SDK_VERSION}-linux-x86_64.tar.gz" \
    && TMP_DIR="$(mktemp -d)" \
    && curl -fL "${DOWNLOAD_URL}" --output "${TMP_DIR}/google-cloud-sdk.tar.gz" \
    && mkdir -p "${GCLOUD_HOME}" \
    && tar xzf "${TMP_DIR}/google-cloud-sdk.tar.gz" -C "${GCLOUD_HOME}" --strip-components=1 \
    && "${GCLOUD_HOME}/install.sh" \
       --bash-completion=false \
       --path-update=false \
       --usage-reporting=false \
       --additional-components alpha beta kubectl \
       --quiet \
    && rm -rf "${TMP_DIR}" \
    && rm -rf "${GCLOUD_HOME}/.install/.backup/" \
    && gcloud --version


WORKDIR $AIRFLOW_HOME

COPY scripts scripts
RUN chmod +x scripts

# Switch to airflow user
USER $AIRFLOW_UID

# ref:https://airflow.apache.org/docs/docker-stack/build.html#adding-a-new-pypi-package
COPY requirements.txt $AIRFLOW_HOME/requirements.txt
RUN pip install --no-cache-dir -r $AIRFLOW_HOME/requirements.txt

