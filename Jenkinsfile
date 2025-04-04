pipeline {
    agent any

    stages {
        stage('Install/Update Packages') {
            steps {
                echo 'Installing required Python packages...'
                sh '''
                    echo "Python version:"
                    python3 --version
                    echo "Pip version:"
                    pip3 --version
                    which pip3

                    python3 -m pip install --upgrade pip

                    pip3 show ncclient    || pip3 install ncclient
                    pip3 show pandas       || pip3 install pandas
                    pip3 show ipaddress    || pip3 install ipaddress
                    pip3 show netaddr      || pip3 install netaddr
                    pip3 show prettytable  || pip3 install prettytable
                '''
            }
        }
    }
}
