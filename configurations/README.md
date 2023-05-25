### Configurations Directory

This directory contains configuration files for the different environments in which your application can run.

##### Files

The following files are included in this directory:

- `.env`: A default environment variables file that should be used when running the application locally.

- `.env.sample`: A sample environment variables file that should be used as a template for setting up environment variables. This file is pushed to the repository so that developers can see the required environment variables for the application.

- `.env.development`: An environment variables file that should be used when running the application in development mode.

- `.env.staging`: An environment variables file that should be used when running the application in staging mode.

- `.env.production`: An environment variables file that should be used when running the application in production mode.

##### Usage

When setting up your application, you should copy the `.env.sample` file to a new file named `.env`, and set the required environment variables. This file should not be pushed to the repository.

When running the application, the appropriate environment variables file should be used based on the mode. For example:

- To run the application in development mode, use the `.env.development` file.
- To run the application in staging mode, use the `.env.staging` file.
- To run the application in production mode, use the `.env.production` file.

The application will automatically load the environment variables from the appropriate file based on the mode.

##### Notes

- It is important to keep environment variables secret, especially in production mode. Make sure to keep your environment variables file secure and do not share it publicly.

- When deploying your application to a server, you should set the environment variables using the server's configuration tool instead of relying on the `.env` file.

- Make sure to update your `.env.sample` file whenever you add new environment variables to the application.
