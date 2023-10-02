# # Pull the base image with python 3.8 as a runtime for your Lambda
# FROM public.ecr.aws/lambda/python:3.8

# # # Install OS packages for Pillow-SIMD
# # RUN yum -y install tar gzip zlib freetype-devel \
# #     gcc \
# #     ghostscript \
# #     lcms2-devel \
# #     libffi-devel \
# #     libimagequant-devel \
# #     libjpeg-devel \
# #     libraqm-devel \
# #     libtiff-devel \
# #     libwebp-devel \
# #     make \
# #     openjpeg2-devel \
# #     rh-python36 \
# #     rh-python36-python-virtualenv \
# #     sudo \
# #     tcl-devel \
# #     tk-devel \
# #     tkinter \
# #     which \
# #     xorg-x11-server-Xvfb \
# #     zlib-devel \
# #     && yum clean all

# # Install ffmpeg

# # 下载并执行安装脚本

# # 安装ffmpeg
# RUN yum -y update
# RUN sed -i 's|^mirrorlist=|#mirrorlist=|g' /etc/yum.repos.d/*.repo && \
#     sed -i 's|^#baseurl=http://mirror.centos.org|baseurl=https://vault.centos.org|g' /etc/yum.repos.d/*.repo
# RUN yum -y install ffmpeg
# RUN mkdir video
# RUN mkdir videoPicture

# # Copy the earlier created app.py file to the container
# COPY handler.py ./
# COPY encoding ./

# RUN python3 -m pip install boto3 pandas ffmpeg-python pickle face_recognition os

# # Set the CMD to your handler
# # CMD ["handler.lambda_handler"]
# CMD ["python3", "handler.py"]



# Define global args
ARG FUNCTION_DIR="/home/app/"
ARG RUNTIME_VERSION="3.8"
ARG DISTRO_VERSION="3.12"

# Stage 1 - bundle base image + runtime
# Grab a fresh copy of the image and install GCC
FROM python:${RUNTIME_VERSION} AS python-alpine

RUN apt-get update \
    && apt-get install -y cmake ca-certificates libgl1-mesa-glx
RUN python${RUNTIME_VERSION} -m pip install --upgrade pip

# Stage 2 - build function and dependencies
FROM python-alpine AS build-image

# Include global args in this stage of the build
ARG FUNCTION_DIR
ARG RUNTIME_VERSION
# Create function directory
RUN mkdir -p ${FUNCTION_DIR}

# Install Lambda Runtime Interface Client for Python
RUN python${RUNTIME_VERSION} -m pip install awslambdaric --target ${FUNCTION_DIR}

# Stage 3 - final runtime image
# Grab a fresh copy of the Python image
FROM python-alpine
# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}
# Copy in the built dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}
# (Optional) Add Lambda Runtime Interface Emulator and use a script in the ENTRYPOINT for simpler local runs
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
RUN chmod 755 /usr/bin/aws-lambda-rie

# Install ffmpeg
RUN apt-get install -y ffmpeg

# Copy handler function
COPY requirements.txt ${FUNCTION_DIR}
RUN python${RUNTIME_VERSION} -m pip install -r requirements.txt --target ${FUNCTION_DIR}
COPY entry.sh /

# Copy function code
COPY handler.py ${FUNCTION_DIR}
RUN chmod 777 /entry.sh

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
# CMD [ "handler.handler" ]
ENTRYPOINT [ "/entry.sh" ]
CMD [ "handler.face_recognition_handler" ]
