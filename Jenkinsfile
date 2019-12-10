
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
sh '''cat <<'EOF' > config
EOF'''
sh '''./scripts/rpm-build.sh'''
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
