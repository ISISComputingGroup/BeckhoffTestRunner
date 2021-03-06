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
    
// at moment use python in EPICS build area
//	stage("Dependencies") {
//        steps {
//          echo "Installing local genie python"
//          timeout(time: 1, unit: 'HOURS') {
//            bat """
//                update_genie_python.bat ${env.WORKSPACE}\\Python
//            """
//          }
//        }
//    }

    stage("Build") {
      steps {
        bat """
            git submodule update --init --recursive --remote
            build.bat
            """
        }
    }

    // We need an EPICS installation, so temporarily link to the one built by newbuildtest
	// Not ideal as newbuildtest may have failed to built
    stage("Test") {
      steps {
	   lock(resource: ELOCK, inversePrecedence: true) {
        timeout(time: 16, unit: 'HOURS') {
         bat """
		    setlocal
		    @echo Temporarily enabling newbuildtest build as system EPICS installation
		    if exist "c:\\Instrument\\apps\\epics" rmdir c:\\Instrument\\apps\\epics
			mklink /j c:\\Instrument\\apps\\epics c:\\jenkins\\workspace\\newbuildtest
            call c:\\Instrument\\apps\\epics\\config_env.bat
			set PYTHONUNBUFFERED=1
		    @echo Starting tests
            python %EPICS_KIT_ROOT%\\support\\IocTestFramework\\master\\run_tests.py -tp ".\\PLC_solution\\tests"
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
