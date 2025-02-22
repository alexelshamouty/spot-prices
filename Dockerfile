FROM public.ecr.aws/lambda/python:3.11
WORKDIR ${LAMBDA_TASK_ROOT}
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt -t ${LAMBDA_TASK_ROOT}
COPY spot_lambda.py ${LAMBDA_TASK_ROOT}
CMD [ "spot_lambda.handler" ]
