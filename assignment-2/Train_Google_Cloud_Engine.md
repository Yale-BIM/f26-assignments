# Training a Neural Network with Google Cloud

There are many ways to train models with Google Cloud, e.g., using a virtual machine in the Compute Engine, using the 
cloud ML Engine, etc. Here, we recommend that you use a Virtual Machine (VM) as that is the closest
setup to working with a local machine.

> All the students that are enrolled in CPSC-4590/5590 will receive a $50 credit for Google Cloud
to use for Assignment 2 or their final project. The credit will be associated
to the student's Yale email. Students should use the resources judiciously. 

## How to claim your BIM credits?

1. Redeem the coupon while signed in to Google Cloud with your yale.edu account. The coupon redemption process will create a billing account ("Billing Account for Education") with the credits on it. Within this billing account, if you go to the "Credits" page, you should see the BIM credits listed as "CPSC 4590/5590 Building Interactive Machines".

2. Create a project: in the Google Cloud console, click New Project, and under Location choose `yale.edu > CPSC-4590`. You may need to search for this folder as "CPSC-4590" in the search bar for project locations.

3. Link your credits: in the new project, go to Billing and link the billing account from step 1.


## WARNING. Make Sure to Stop Your VM Instances!

Don’t forget to **stop your VM instance** when you are done 
(by clicking on the stop button at the top of the page showing your instances), 
otherwise you will run out of credits. 


<img src="docs/no-more-credits.jpeg" width="300"/><br/>
(image created by Gemini 3.6 Thinking)

## Getting Started with the Compute Engine of Google Cloud

1. Go to the http://cloud.google.com/
website, and **log in with your Yale email.** Then, go to your Console and select your new project for the BIM course, which has the credits linked to it as explained earlier in this document.
   
2. Follow the steps in [this tutorial](https://docs.cloud.google.com/compute/docs/create-linux-vm-instance) to create a Virtual Machine (VM). This will require you to enable the Compute Engine API in Google Cloud, before you can create a VM instance. As a reference for Assignment 2, a Virtual Machine from Google Cloud with the following specifications is enough:

    - **Name:** bim-a2
    - **Region:** us-central1 (Iowa)
    - **Zone:** Any
    - **Machine Family:** GPUs
    - **Series:** N1
    - **GPU Type:** 1 x NVIDIA T4
    - **Machine Type:** n1-standard-4 (4 vCPU, 15 GB Memory)
    - **VM Provisioning Model:** Standard

    > When setting up the options above, you may see a message on the right side of the Google Cloud interface that indicates that you need to update your GPU quota. Request an upgrade for the quota. This is handled by Google Cloud automatically, and it could take up to 2 days to process.

    For the VM, we also recommend that you set these options:

    - **Allow HTTP** and **Allow HTTPS** traffic so that you can connect to the Internet from the machine.
    - **Boot disk:** Ubuntu 24.04 LTS
    - **Boot disk type:** SSD persistent disk (50 GB)

    > The cost for such a virtual machine should be around $0.25 per hour.
    
4. You should then be able to connect to your virtual machine over SSH on your browser.

    > To connect directly through a shell in your local machine, you will need to install the
    [gcloud sdk](https://cloud.google.com/sdk/gcloud/) and follow [these instructions](https://cloud.google.com/compute/docs/connect/standard-ssh#gcloud_1).


## Working With Your VM in Google Cloud

Once you've created your VM in Google Cloud. You can download your code from GitHub as usual
and commit back things to your repository as necessary. 

### TensorBoard 
It is also possible to use port forwarding (as discussed in [here](https://www.apoehlmann.com/blog/connecting-tensorboard-your-google-cloud-vm-port-forwarding/#:~:text=PC-,So,6006%2E,-For)) to 
run TensorBoard on a Google Cloud VM and visualize your results on a local browser.
To succeed running the steps below, you will need to install the [Google Cloud (gcloud) sdk](https://cloud.google.com/sdk/gcloud/).

1. On a terminal in your host machine, authenticate and log into your VM:
    ```bash
    $ gcloud auth login
    $ gcloud compute ssh <vm-name> --zone <zone>
    ```
    > Tip: You can avoid passing `--zone` every time by running `gcloud config set compute/zone <zone>`.
    If you have multiple Google Cloud projects, also pass `--project <project-id>`.

2. On the VM (inside the SSH session from step 1), start TensorBoard on port 6006:
    ```bash
    $ tensorboard --logdir <path_to_logs> --port 6006
    ```

3. Open another terminal in your host machine and forward your local port 6006 to port 6006 on the VM:
    ```bash
    $ gcloud compute ssh <vm-name> --zone <zone> -- -NfL 6006:localhost:6006
    ```
    The `-L` flag sets up local port forwarding through SSH, `-N` tells SSH not to run a remote command,
    and `-f` sends the tunnel to the background. Because the connection goes through SSH, you do not
    need to open port 6006 in the VM's firewall.

4. Finally, in your browser navigate to: 
    ```
    http://localhost:6006/
    ```

5. When you are done working, stop TensorBoard on the VM by pressing `Ctrl+C` in the terminal where it is running.
Then, close the SSH tunnel on your host machine. Because the tunnel was sent to the background (`-f`), closing
the terminal does not stop it, so you need to kill the process explicitly:
    ```bash
    $ pkill -f "6006:localhost:6006"
    ```
    You can verify that the tunnel is gone by checking that no process is listening on port 6006 anymore 
    (the command below should print nothing):
    ```bash
    $ lsof -i :6006
    ```
    > Tip: Remember to also stop your VM from the Google Cloud console (or with `gcloud compute instances stop <vm-name> --zone <zone>`)
    when you are not using it, so you don't use up your credits.
    


