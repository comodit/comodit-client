
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
sh '''cat <<'EOF' > config
EOF'''
sh '''./scripts/build-rpm.sh'''
            }
        }
        stage('SSH Transfer') {
            steps {
                echo 'Testing..'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
            }
        }
    }
}
