﻿using System;
using EnvDTE;
using TCatSysManagerLib;

namespace AutomationTools
{
    class Builder
    {
        private Solution solution;
        private Utils utils;

        /// <summary>
        /// Class that builds the project.
        /// </summary>
        /// <param name="solution">The solution to build.</param>
        /// <param name="utils">A utils instance that has various utilities.</param>
        public Builder(Solution solution, EnvDTE80.DTE2 dte)
        {
            this.solution = solution;
            this.utils = new Utils(dte);
        }

        /// <summary>
        /// Builds the specified solution.
        /// </summary>
        /// <returns>true if build was successful, false otherwise</returns>
        public Boolean buildSolution() {
            Console.WriteLine("Started Build");
            solution.SolutionBuild.Build();

            vsBuildState state = solution.SolutionBuild.BuildState;
            while (state == vsBuildState.vsBuildStateInProgress)
            {
                System.Threading.Thread.Sleep(1000);
                state = solution.SolutionBuild.BuildState;
                this.utils.printErrors();
            }

            return (solution.SolutionBuild.LastBuildInfo == 0 && state == vsBuildState.vsBuildStateDone);
        }

        /// <summary>
        /// Builds the specified solution.
        /// </summary>
        /// <returns>true if build was successful, false otherwise</returns>
        public Boolean cleanSolution()
        {
            Console.WriteLine("Started Clean");
            solution.SolutionBuild.Clean();

            vsBuildState state = solution.SolutionBuild.BuildState;
            while (state == vsBuildState.vsBuildStateInProgress)
            {
                System.Threading.Thread.Sleep(1000);
                state = solution.SolutionBuild.BuildState;
                this.utils.printErrors();
            }

            return (solution.SolutionBuild.LastBuildInfo == 0 && state == vsBuildState.vsBuildStateDone);
        }

        /// <summary>
        /// Sets the PLC project to autostart on boot. This is required for automated testing.
        /// </summary>
        /// <param name="project">The project to set to autoboot.</param>
        private void setProjectToBoot(ITcPlcProject project)
        {
            project.BootProjectAutostart = true;
            project.GenerateBootProject(true);
        }

        /// <summary>
        /// Checks that a solution contains at least one PLC project.
        /// </summary>
        /// <returns>The project that can be run</returns> 
        public Project findPLCProject()
        {
            foreach (Project project in solution.Projects)
            {
                try
                {
                    ITcSysManager4 twinCatProject = (ITcSysManager4)project.Object;
                    ITcSmTreeItem plcConfig = twinCatProject.LookupTreeItem("TIPC");
                    foreach (ITcSmTreeItem PLCProject in plcConfig)
                    {
                        // Assume you want to run the all PLCs
                        setProjectToBoot((ITcPlcProject)PLCProject);
                        Console.WriteLine("Found PLC Project: " + project.Name + "." + PLCProject.Name);
                    }
                    return project;
                } catch {
                    Console.WriteLine(project.Name + " is not a Twincat project");
                }
            }
            return null;
        }
    }
}
