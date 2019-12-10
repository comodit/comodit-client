
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
                                     execCommand: "${EXEC_COMMAND}",
                                     execTimeout: 120000, 
                                     flatten: false,
                                     makeEmptyDirs: false,
                                     noDefaultExcludes: false,
                                     patternSeparator: '[, ]+',
                                     remoteDirectory: "${REMOTE_PATH}",
                                     remoteDirectorySDF: false,
                                     removePrefix: "${SOURCE_PATH}",
                                     sourceFiles: "${SOURCE_PATH}*.rpm")],
                                 usePromotionTimestamp: false,
                                 useWorkspaceInPromotion: false,
                                 verbose: false
                             )])
            }
        }
        stage('Update') {
            steps {
withCredentials([string(credentialsId: '75098809-de38-4e65-92ae-428395cf8ba2', variable: 'TOKEN')]) {
sh "comodit --api https://my.comodit.com/api --token $TOKEN hosts applications actions run ${ACTION}"
    }
            }
        }
    }
}
