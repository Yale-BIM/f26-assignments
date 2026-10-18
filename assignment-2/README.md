# Assignment 2

This is the second assignment for Yale's CPSC-4590/5590 Building Interactive Machines course.

## Table of Contents

* [Introduction](#introduction)
    * [System Requirements](#system-requirements)
    * [Background Knowledge](#background-knowledge)
    * [Preliminaries](#preliminaries)
    * [Deliverables](#deliverables)
    * [Evaluation](#evaluation)
* [Setup](#setup)
* [Part I. Approximating a Non-Linear Function](#part-i-approximating-a-non-linear-function)
* [Part II. Imitation Learning (2 extra points)](#part-ii-imitation-learning-2-potential-extra-points)
* [Part III. Real-Time Filtering](#part-iii-real-time-filtering)
* [Parts IV and V](#parts-iv-and-v)


## Introduction 
This assignment will provide you practical experience with deep learning. In particular, you'll become familiar with [PyTorch API](https://docs.pytorch.org/docs/2.14/pytorch-api.html).


#### System Requirements
This assignment should be completed using Python 3.12 in Ubuntu 24.04. For training neural networks, we recommend that you use cloud services if your don't have access to a local GPU. For the last part of the assignment, you should have access to a computer with `ROS 2 Jazzy`.

You should also have `git` and `pip3` installed in the machine that you are using to work on your assignment.
You will use git to save your work to your [Github](http://www.github.com) repository. The pip3 tool will be used to install
Python dependencies, and can be installed in Ubuntu 24.04 with `sudo apt install python3-pip`--this should already be installed in the Zoo and the bim laptops.

#### Background Knowledge

This assignment assumes that you have already completed the prior assignments and, thus, you have experience with Linux shells 
(e.g., [bash](https://www.gnu.org/software/bash/)), and [git](https://git-scm.com/). You are also expected to be familiar with the [numpy Python library](http://www.numpy.org/) for linear algebra. 
If you are not, please check [this tutorial](https://docs.scipy.org/doc/numpy/user/quickstart.html) before starting the assignment.

#### Preliminaries
You will be training supervised learning models, especially Neural Networks, for this assignment. 
It is possible to complete the training of models using your local CPU, but it might be faster at times to train on the cloud and
using hardware acceleration (e.g., a dedicated GPU).

> Whether or not you use the cloud to train your neural networks, the deliverables are the same.
You should submit code in your private Github repository. You should also submit a report to Gradescope and provide model parameter files through Google Drive.

#### Deliverables

- **Report:** You are expected to answer questions in Gradescope at the end of each part of the assignment. This online report should also have the specific commit SHA of the version of the code that you submit for the assignment. 

- **Model weights and input normalization parameters:** You should upload trained models and parameters to Google Drive and share them with anybody who has access to the links.

- **Code:** Finally, you are expected to push code for this assignment to your 
[Github](http://www.github.com) repository and submit it to Gradescope.

#### Evaluation

You assignment will be evaluated based on the content of your report and your code.

- Report (52 pts for CPSC-4590 / 72 pts for CPSC-5590)
    * Part I (32 pts): I-1 (8 pts) + I-3 (8 pts) + I-4 (10 pts) + I-5 (6 pts)
    * Part III (20 pts): IV-1 (5 pts) + IV-2 (5 pts) + IV-3 (5 pts) + IV-4 (5 pts)
    * Part V (20 pts for CPSC-5590 only): IV-1 (7 pts) + IV-2 (5 pts) + IV-3 (8 pts)
- Code (128 pts for CPSC-4590 / 148 pts for CPSC-5590)
    * Part I (20 pts): I-1 (4 pts) + I-2 (6 pts) + I-3 (10 pts)
    * Part II (54 pts): II-1 (34 pts) + II-2 (20 pts)
    * Part III (54 pts): III-5 (8 pts) + III-6 (8 pts) + III-7 (6 pts) + III-8 (6 pts) + III-9 (4 pts) + III-10 (6 pts) + III-11 (16 pts) 
    * Part IV (20 pts for CPSC-5590 only): IV-1 (20 pts)

Students taking CPSC-4590 will be evaluated over 180 pts. Those taking CPSC-5590, will be evaluated over 220 pts.

**Note on Part II of the assignment:** Part II provides extra credit for the students that obtain best performance in this part of the assignment. The extra credit (1 pts) will be counted for the final course grade 
(beyond whatever points students get for this assignment). 

## Setup
Before you start implementing or answering questions for this assignment, please update your repository to pull the latest changes from the assignments repository, install Python dependencies, and update the `shutter-ros2` repository. 

The `install_python_deps.sh` script installs PyTorch 2.14.1 from PyPI. That build runs on the CPU, and on NVIDIA GPUs from the Turing generation (RTX 20xx) onward. If your machine has an older Pascal GPU like the GTX 1080/1070, edit the script to use the commented-out CUDA 12.6 install command instead.

```bash
# create a Python virtual environment in your workspace (only needed once).
# --system-site-packages keeps the ROS 2 Python packages visible inside the environment.
$ cd <path-to-your-ros2-workspace>
$ python3 -m venv --system-site-packages .venv

# activate your Python virtual environment
$ source .venv/bin/activate

# update your repository with the latest version of the assignment
$ cd <path-to-your-repository-in-your-workspace>
$ git pull upstream master

# install Assignment-2 Python dependencies in your virtual environment
$ cd assignment-2
$ ./install_python_deps.sh

# update the shutter-ros2 repository 
$ cd <path-to-your-ros2-workspace>/src/shutter-ros2
$ git pull

# finally, build your ROS 2 workspace 
$ cd <path-to-your-ros2-workspace>
$ colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release
```

You can verify your PyTorch installation as follows:

```bash
$ python3 -c "import torch; print(torch.__version__)"
(...)
2.14.1+cu130
```

The suffix after the `+` sign tells you which build you installed (e.g., `cu130` or `cu126` for CUDA 13.0 or 12.6, or `cpu`).

**NOTE:** If your machine has a GPU with NVIDIA driver, then you can take advantage of hardware acceleration. You can test that your GPU is visible in PyTorch by running the following commands on a Python shell:

```python
>> import torch
>> torch.cuda.is_available()
```

## Part I. Approximating a Non-Linear Function

Read the [Primer on Universal Function Approximation](FunctionApproximationPrimer.md) that is included in this assignment.

Once you've read the primer, you should complete the tasks below to approximate the 
[monkey saddle surface](https://en.wikipedia.org/wiki/Monkey_saddle) defined by the equation ![equation](https://latex.codecogs.com/gif.latex?z&space;=&space;x^3&space;-&space;3xy^2).
<!-- $`z = x^3 - 3xy^2`$ --> 
Your code should leverage [PyTorch API](https://docs.pytorch.org/docs/stable/index.html).

To get you started, this assignment provides two files within the 
`assignment-2/function_approximation` directory:

- *train_and_test_saddle_function.py:* main file that you will complete in this part of the assignment.
- *saddle_function_utils:* code to generate data and help you visualize results.

If you run the `train_and_test_saddle_function.py` script (which is incomplete at this point)
with the `visualize_training_data` option, you should be able to visualize the data that the
script generates for you and example predictions with a linear neural network model implemented with 
[PyTorch API](https://docs.pytorch.org/docs/stable/index.html):

```bash
$ cd assignment-2/function_approximation
$ ./train_and_test_saddle_function.py --visualize_training_data
```

When you run the script, a [matplotlib](https://matplotlib.org/) plot of the data should appear, 
as in the figure below:

<img src="docs/training-val-data.png" width="600"/>

And, once the linear model is trained for a number of epochs with the 
[Adam optimizer](https://docs.pytorch.org/docs/stable/generated/torch.optim.Adam.html), the script would show a figure like the one below:

<img src="docs/fit-linear.png" width="600"/>

To see all the options that the train script already provides, run it as:

```bash
$ ./train_and_test_saddle_function.py --help
usage: train_and_test_saddle_function.py [-h] [--n N]
                                         [--batch_size BATCH_SIZE]
                                         [--epochs EPOCHS] [--lr LR]
                                         [--visualize_training_data]
                                         [--build_fn BUILD_FN]

optional arguments:
  -h, --help            show this help message and exit
  --n N                 total number of examples (including training, testing,
                        and validation)
  --batch_size BATCH_SIZE
                        batch size used for training
  --epochs EPOCHS       number of epochs for training
  --lr LR               learning rate for training
  --visualize_training_data
                        visualize training data
  --build_fn BUILD_FN   model to train (e.g., 'linear')
```

The optional parameters `lr`, `epochs`, and `batch_size` correspond to the learning rate,
number of epochs, and bath size that are used at training time.

Read the code in the training script to familiarize yourself with its functionality. 

### Questions/Tasks

- **I-1.** Add logging and checkpointing functionality to the `train_model()` method of the `train_and_test_saddle_function.py` script:

    
    ```python
    # Setup logging
    logs_dir = 'logs/log_{}'.format(datetime.datetime.now().strftime("%m-%d-%Y-%H-%M"))
    os.makedirs(logs_dir, exist_ok=True)
    writer = SummaryWriter(log_dir=logs_dir)

    # Add model graph to TensorBoard
    # Create a dummy input with the same shape as training data
    dummy_input = torch.as_tensor(norm_train_input[:1], dtype=torch.float32).to(device)  # Use first sample as dummy input; add_graph below only traces the model's operations
    writer.add_graph(model, dummy_input)

    best_val_loss = float('inf')
    best_model_path = os.path.join(logs_dir, 'best_monkey_weights.pth')

    # Training loop
    for epoch in range(epochs):
        ...
        # Log to tensorboard
        writer.add_scalar('Loss/Train', avg_train_loss, epoch)
        writer.add_scalar('Loss/Val', avg_val_loss, epoch)
        writer.add_scalar('MAE/Train', avg_train_mae, epoch)
        writer.add_scalar('MAE/Val', avg_val_mae, epoch)
        
        # Save best model
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            torch.save(model.state_dict(), best_model_path)

    # After the training loop, close the writer so that all logs are written to disk
    writer.close()

    # Load best model
    model.load_state_dict(torch.load(best_model_path, weights_only=True))
    ```

    The logging and checkpointing functionality performs the following operations during the training loop:
    
    - **SummaryWriter:** The [PyTorch TensorBoard](https://pytorch.org/docs/stable/tensorboard.html) 
    writer logs training metrics to a given directory for visualization.
    - **Model Checkpointing:** The code saves the model state dict after every epoch if the
    validation loss is smaller than the prior best validation loss. The model is saved using PyTorch's
    `torch.save()` function with the `.pth` extension. After training, the best model is loaded back so that
    it is the one used for testing.<br/><br/>
    
    Run the `train_and_test_saddle_function.py` script again to check that it is indeed saving model weights to a logs folder.
    Also, check that you can visualize your training losses in TensorBoard by running it from another shell:

    ```bash
    $ tensorboard --logdir <path_to_logs>
    ```

    Then, go to the URL that the script provides (e.g., http://localhost:6006) in your favorite
    browser. The `SCALARS` tab of the TensorBoard interface should then show various training curves
    (e.g., Loss/Train, Loss/Val, MAE/Train, MAE/Val for the loss and mean absolute error after every epoch in the training and validation sets). The `GRAPHS` tab of the TensorBoard interface should show a 
    [computation graph](https://www.tensorflow.org/tensorboard/graphs) for your simple neural network model.
    
    Double-click all nodes in the graph to expand them, and then make a screenshot of your computation graph and include it in your project report.
    
    > NOTE: In general, we recommend that you use TensorBoard to check your models' computation
    graphs and training/validation performance for all of the other tasks in this assignment. 
    This 30min [TensorBoard tutorial](https://www.youtube.com/watch?v=eBbEDRsCmv4) from 2017
    provides good examples on how the interface can help you debug many issues! Since that date, many kinds of visualization types have been added to TensorBoard--check them out [here](https://pytorch.org/docs/stable/tensorboard.html#torch.utils.tensorboard.writer.SummaryWriter).
    
- **I-2.** Modify the `train_and_test_saddle_function.py` script so that you can load a `pre-trained model` 
and train its weights further (e.g., to resume training or for fine-tuning on a new task).

    a. Add a "load_model" argument to the argument parser at the end of the script:
        
    ```python
    parser = argparse.ArgumentParser()
    ... # other arguments
    parser.add_argument("--load_model", help="path to the model",
                        type=str, default="")
    ```
        
    b. Add code after the `build_fn` variable is set at the end of the script to
    replace the value of `build_fn` with [PyTorch's model loading functionality](https://pytorch.org/docs/stable/generated/torch.load.html):
    
    ```python
    ... # Set ArgumentParser arguments()
    
    # define the model function that we will use to assemble the Neural Network
    if args.build_fn == "linear":
    ...
        
    # ---- lines to be added ----
    # load model (and thus, ignore prior build function)
    if len(args.load_model) > 0:
        # Store the original build_fn before overriding it
        original_build_fn = build_fn

        def load_pytorch_model(num_inputs):
            # Use the build_fn parameter to determine model type
            model = original_build_fn(num_inputs)
            # Load state dict
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            model.load_state_dict(torch.load(args.load_model, map_location=device, weights_only=True))
            return model

        build_fn = load_pytorch_model
    # ---- end of lines to be added ----
        
    # run the main function
    main(args.n, args.epochs, args.lr, args.visualize_training_data, build_fn=build_fn, batch_size=args.batch_size)
    sys.exit(0)
    ```
        
    > Note that the PyTorch model loading uses `torch.load()` to load the state dictionary, which contains
    the model's weights and biases. The model architecture is first created using the build_fn, then the pre-trained weights are loaded using `model.load_state_dict()`. 
    With `weights_only=True` (the default since PyTorch 2.6), `torch.load()` only accepts tensors and basic Python types,
    so it can load a state dictionary but not an arbitrary pickled Python object.
        
    c. Test your code. Your script should now be able to load a model from a file and continue training
    its weights thereafter:
    
    ```bash
    $ ./train_and_test_saddle_function.py --load_model <path_to_model_pth_file> [--lr 1e-2] [--epochs 500] [--batch_size 16]
    ```
    
    The model that you trained before for task I-1 should be stored as `best_monkey_weights.pth`
    within the folder corresponding to your training session in `assignment-2/function_approximation/logs`.
    You can pass this model as argument to your `train_and_test_saddle_function.py` to test the new functionality that you just implemented.
    
- **I-3.** Complete the function called `build_nonlinear_model()` in the `train_and_test_saddle_function.py` 
script. This function should have as argument the number of input features for the data and should
return a [PyTorch model](https://pytorch.org/docs/stable/generated/torch.nn.Module.html), similar to the `build_linear_model()` function that you implemented before. The difference between these functions, though, is that `build_nonlinear_model()` should implement a more complex neural network capable of approximating the monkey saddle surface with an **average L2 error of 150 or less on the test set**. Note that this error is printed by the `train_and_test_saddle_function.py` script when it finishes running.

   The `build_nonlinear_model()` function looks as follows in the `train_and_test_saddle_function.py` script:

    ```python
    def build_nonlinear_model(num_inputs):
    """
    Build nonlinear NN model with PyTorch
    :param num_inputs: number of input features for the model
    :return: PyTorch model
    """
    ... # complete
    ```
    
    Once you've implemented the function, edit the last lines of the `train_and_test_saddle_function.py` 
    script to be able to change the model that is trained through the command line:
    
    ```python
    # define the model function that we will use to assemble the Neural Network
    if args.build_fn == "linear":
        build_fn = build_linear_model # function that builds linear model
    elif args.build_fn == "nonlinear":
        build_fn = build_nonlinear_model # function that builds non-linear model
    else:
        print("Invalid build function name {}".format(args.build_fn))
        sys.exit(1)
    ```
    
    You should then be able to train and test your model as:
    ```bash
    $ ./train_and_test_saddle_function.py --build_fn nonlinear [--lr 1e-1] [--epochs 10] [--batch_size 16]
    ```
    
    Change your nonlinear model, the learning rate, and number of epochs that you are training for
    until you achieve an average test error of 150 or less. Afterwards, take a new screenshot of the plot
    that you get after training. This plot should be similar to [docs/fit-linear.png](docs/fit-linear.png)
    but show the result for your new nonlinear model. In summary, include in your report:
     
    - The screenshot of the plot with test results after training;
    - what average L2 error did you get on the test set this time;
    - a description of the neural network model that you used to approximate the monkey saddle surface; and
    - whatever parameters you used for training it (e.g., batch size, learning rate, and number of epochs).<br/><br/>
    
- **I-4.** Train your nonlinear neural network such that it `overfits` on the training data. 

    After training, include a picture
    in your report of the plots from TensorBoard corresponding to the `mean absolute error` (mae) on the training and validation
    sets. Explain how you concluded that your model overfit in the report.
    
- **I-5.** What happens with the loss per epoch on the training set if you train with a batch size of 1?
Explain why does the loss per epoch graph look different than with a bigger batch size (e.g., than with a batch size of 100).
