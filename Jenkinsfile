pipeline {
  agent any
  stages {
    stage('检出') {
      steps {
        checkout([
          $class: 'GitSCM',
          branches: [[name: GIT_BUILD_REF]],
          userRemoteConfigs: [[
            url: GIT_REPO_URL,
            credentialsId: CREDENTIALS_ID
          ]]])
        }
      }
      stage('登录镜像仓库') {
        steps {
          withCredentials([ usernamePassword(credentialsId:'972d15e3-aa23-4c7c-acdc-7eef031ee32e',usernameVariable:'USERNAME',passwordVariable:'PASSWORD')
        ]) {
          sh 'docker login -u ${USERNAME} -p ${PASSWORD} registry-ze.tencentcloudcr.com``'
        }

      }
    }
    stage('构建镜像') {
      steps {
        sh 'ls'
        sh "docker build -t ${DOCKER_REPOSITORY_NAME}:${DOCKER_IMAGE_NAME}  -f ${DOCKERFILE_PATH} ."
      }
    }
    stage('推送镜像') {
      steps {
        script {
          docker.withRegistry("https://${DOCKER_REGISTRY_HOSTNAME}", "${DOCKER_REGISTRY_CREDENTIAL}") {
            docker.image("${DOCKER_REPOSITORY_NAME}:${DOCKER_IMAGE_NAME}").push()
          }
        }

      }
    }
  }
  environment {
    DOCKER_REGISTRY_HOSTNAME = "${TCR_REGISTRY_HOSTNAME}"
    DOCKER_REGISTRY_CREDENTIAL = "${TCR_REGISTRY_CREDENTIAL}"
    DOCKER_REPOSITORY_NAME = "registry-ze.tencentcloudcr.com/${TCR_NAMESPACE_NAME}/${TCR_REPOSITORY_NAME}"
    DOCKER_IMAGE_NAME = "${TCR_IMAGE_NAME}"
  }
}