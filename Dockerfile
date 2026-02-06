FROM python:3.9

ARG GROUP_ID=1000
ARG GROUP=adl
ARG USER_ID=1000
ARG PY_USER=adl
ARG WD=my-adl-project

RUN groupadd -g ${GROUP_ID} ${GROUP}
RUN adduser --disabled-password --gecos '' --uid ${USER_ID} ${PY_USER} --ingroup ${GROUP}

ENV PATH="/home/${PY_USER}/.local/bin:${PATH}"

USER $PY_USER

WORKDIR /home/${PY_USER}/${WD}
COPY requirements.txt .
RUN pip install -U -r requirements.txt

CMD ["python", "dataloader.py"]
