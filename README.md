# SWVL: An AI-powered face tracking camera gimbal.

This GitHub repo contains all of the files for the SWVL gimbal hardware and software. SWVL was created by me (Alex Anderson-McLeod), Kuba Jerzmanowski, Jagger Tanner, Trevor Allison, and Michael Laitarovsky as our senior Capstone project at the University of South Carolina.

Most of the files in the root directory were for testing purposes and can be ignored. All of the SWVL software for the host computer, including the Electron frontend and Python backend, are in the sw directory, and everything hardware-related (the CAD files for the gimbal itself, the control PCB design, and the code running on the control board) can be found in the hw directory.

The one file in the root directory that might actually be useful to you is SWVL_Paper.pdf. This paper describes the entire project in great detail, covering our objectives, methodology, and results.

We were unable to upload the model itself to GitHub because of its large size, so you can find it [here](https://emailsc-my.sharepoint.com/:f:/g/personal/aja4_email_sc_edu/ErGuz_QFEuFKh9op3Ph_HMUBoIsI0FKV3FtuGb-c4GJ2zg?e=ibyNqy) instead. For some stupid reason, USC has disabled the "anyone with the link can view" option when sharing files in OneDrive, so this link will only work for other people from the university. I have no idea why they would do this, but if you're outisde the university and want access, send me an email and I'll get you the files. The latest one is best_dev_loss0476_dsc.pth, but there are also older versions in that directory if you're interested in the improvements we made throughout the development process.
