pipeline {
    agent any

    stages {
        stage('Install/Update Packages') {
            steps {
                sh '''
                    pip3 show ncclient || pip3 install ncclient
                    pip3 show pandas || pip3 install pandas
                    pip3 show ipaddress || pip3 install ipaddress
                    pip3 show netaddr || pip3 install netaddr
                    pip3 show prettytable || pip3 install prettytable
                '''
            }
        }

        stage('PEP8 Style Check (pylint)') {
            steps {
                sh '''
                    pip3 show pylint || pip3 install pylint
                    if [ ! -f netman_netconf_obj2.py ]; then
                        echo "File netman_netconf_obj2.py not found!"
                        exit 1
                    fi
                    pylint netman_netconf_obj2.py --fail-under=5
                '''
            }
        }
        stage('Run Application') {
            steps {
            echo 'Running netman_netconf_obj2.py...'
                sh '''
                    if [ ! -f netman_netconf_obj2.py ]; then
                    echo "python file is not found!"
                    exit 1
                    fi
                    python3 netman_netconf_obj2.py
                '''
    }
}
        stage('Unit Test') {
            steps {
            echo 'Running unit tests...'
                sh '''
                python3 -m unittest test_netman_lab9.py
                '''
    }
}

    }
}
