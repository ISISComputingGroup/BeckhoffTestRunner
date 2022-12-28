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
   // Checkout done automagically, with submodule recursive update

    stage("Build") {
      steps {
        bat """
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
		    call run_tests.bat -tm DEVSIM
		    set errcode=%errorlevel%
		    rmdir c:\\Instrument\\apps\\epics
		    if %errcode% neq 0 exit /b %errcode%
            """
        }
	   }
	  }
    }
  }
  
  post {
    always {
      bat """
          robocopy "C:\\Instrument\\Var\\logs\\IOCTestFramework" "%WORKSPACE%\\test-logs" /E /R:2 /MT /NFL /NDL /NP /NC /NS /LOG:NUL
          exit /b 0
      """
      archiveArtifacts artifacts: 'test-logs/*.log', caseSensitive: false
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
    timestamps()
  }
}
