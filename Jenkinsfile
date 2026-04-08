pipeline {
    agent any

    environment {
        AWS_ACCESS_KEY_ID     = credentials('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
        GROQ_API_KEY          = credentials('GROQ_API_KEY')
        GITHUB_TOKEN          = credentials('GITHUB_TOKEN')
        AWS_REGION            = 'ap-south-1'
        ECR_REGISTRY          = '940031346109.dkr.ecr.ap-south-1.amazonaws.com'
        ECR_REPO              = 'ai-test-generator'
        GITOPS_REPO           = 'github.com/SannidhiSriram-06/ai-test-generator-gitops.git'
        VALUES_FILE           = 'charts/ai-test-generator/values.yaml'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --quiet -r requirements.txt
                    pip install --quiet pytest pytest-cov
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    export GROQ_API_KEY=$GROQ_API_KEY
                    pytest tests/ --cov=app --cov-fail-under=70 --cov-report=xml --junit-xml=test-results.xml -v
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('Build & Push to ECR') {
            steps {
                sh '''
                    IMAGE_TAG="${BUILD_NUMBER}-$(git rev-parse --short HEAD)"
                    echo "Building image: $ECR_REGISTRY/$ECR_REPO:$IMAGE_TAG"
                    aws ecr get-login-password --region $AWS_REGION | \
                        docker login --username AWS --password-stdin $ECR_REGISTRY
                    docker build -t $ECR_REGISTRY/$ECR_REPO:$IMAGE_TAG .
                    docker push $ECR_REGISTRY/$ECR_REPO:$IMAGE_TAG
                    docker tag $ECR_REGISTRY/$ECR_REPO:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPO:latest
                    docker push $ECR_REGISTRY/$ECR_REPO:latest
                    echo $IMAGE_TAG > image_tag.txt
                '''
            }
        }

        stage('Update GitOps Repo') {
            steps {
                sh '''
                    IMAGE_TAG=$(cat image_tag.txt)
                    git clone https://$GITHUB_TOKEN@$GITOPS_REPO gitops-repo
                    cd gitops-repo
                    sed -i "s|tag: .*|tag: \"$IMAGE_TAG\"|" $VALUES_FILE
                    git config user.email "jenkins@ci"
                    git config user.name "Jenkins"
                    git add $VALUES_FILE
                    git commit -m "ci: update image tag to $IMAGE_TAG [skip ci]"
                    git push
                '''
            }
        }
    }

    post {
        success {
            echo "Pipeline succeeded! Image deployed via ArgoCD."
        }
        failure {
            echo "Pipeline failed. Check console output above."
        }
        always {
            cleanWs()
        }
    }
}
