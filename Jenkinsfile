stage('PEP8 Style Check (pylint)') {
    steps {
        echo 'Checking code style with pylint...'
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
