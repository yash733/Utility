FROM python:3.12

WORKDIR /personal_utility

COPY . /personal_utility

RUN pip install -r ./requirements.txt

EXPOSE 8501

CMD ["streamlit","run","ui/app.py"]