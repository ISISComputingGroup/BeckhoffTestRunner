#!groovy

pipeline {

  // agent defines where the pipeline will run.
  agent {  
    label {
      label "twinCAT"
    }
  }
  
  triggers {
    pollSCM('H/2 * * * *')
  }
  
  environment {
      NODE = "${env.NODE_NAME}"
      ELOCK = "epics_${NODE}"
  }

  stages {  
    stage("Checkout") {
      steps {
        echo "Branch: ${env.BRANCH_NAME}"
        checkout scm
      }
    }

    stage("Build") {
      steps {
        bat """
	    setlocal
	    git clean -fdX PLC_solution/
	    git stash PLC_solution/
            git submodule update --init --recursive --remote --force
            build.bat
            """
        }
    }
    // We need an EPICS installation, so temporarily link to the local one
    // Not ideal as it may have failed to built
    stage("Test") {
      steps {
	   lock(resource: ELOCK, inversePrecedence: false) {
        timeout(time: 16, unit: 'HOURS') {
         bat """
		    setlocal
		    @echo Temporarily enabling EPICS_IOC_Windows10_x64_CLEAN build as system EPICS installation
		    if exist "c:\\Instrument\\apps\\epics" rmdir c:\\Instrument\\apps\\epics
			mklink /j c:\\Instrument\\apps\\epics C:\\Jenkins\\workspace\\EPICS_IOC_Windows10_x64_CLEAN
            call c:\\Instrument\\apps\\epics\\config_env.bat
			set PYTHONUNBUFFERED=1
		    @echo Starting tests
            %PYTHON3% %EPICS_KIT_ROOT%\\support\\IocTestFramework\\master\\run_tests.py -tp ".\\tests"
		    rmdir c:\\Instrument\\apps\\epics
            """
        }
	   }
	  }
    }
  }
  
  post {
    always {
      junit "test-reports/**/*.xml"
    }	
    failure {
      step([$class: 'Mailer', notifyEveryUnstableBuild: true, recipients: 'icp-buildserver@lists.isis.rl.ac.uk', sendToIndividuals: true])
    }
    changed {
      step([$class: 'Mailer', notifyEveryUnstableBuild: true, recipients: 'icp-buildserver@lists.isis.rl.ac.uk', sendToIndividuals: true])
    }
  }
  
  // The options directive is for configuration that applies to the whole job.
  options {
    buildDiscarder(logRotator(numToKeepStr:'5', daysToKeepStr: '7'))
    timeout(time: 60, unit: 'MINUTES')
    disableConcurrentBuilds()
  }
}
