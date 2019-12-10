
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
        stage('Deploy') {
            steps {
                sshPublisher(publishers:
                             [sshPublisherDesc(
                                 configName: "${PUBLISH_NAME}",
                                 transfers: [sshTransfer(
                                     cleanRemote: false,
                                     excludes: '',
                                     execCommand: '',
                                     execTimeout: 120000, 
                                     flatten: false,
                                     makeEmptyDirs: false,
                                     noDefaultExcludes: false,
                                     patternSeparator: '[, ]+',
                                     remoteDirectory: "${REMOTE_PATH}",
                                     remoteDirectorySDF: false,
                                     removePrefix: "${SOURCE_PATH}",
                                     sourceFiles: "${SOURCE_PATH}"*.rpm)],
                                 usePromotionTimestamp: false,
                                 useWorkspaceInPromotion: false,
                                 verbose: false
                             )])
            }
        }
        stage('Update') {
            steps {
                echo 'Deploying....'
            }
        }
    }
}
