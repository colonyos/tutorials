# Getting started
In this tutorial, we will explore how ColonyOS can be used for processing Earth Observation (EO) data. We are going to use a service called [OpenEO](https://openeo.org), which is a service part of the [Digital Earth Sweden](https://digitalearth.se) platform. By combining the capabilities of ColonyOS with the advanced features offered by OpenEO, we will demonstrate how to efficiently handle, analyze, and derive valuable insights from large-scale geospatial datasets.

<img src="arch.png">

# Use case
We will develop an EO workflow with the following steps:

1. Download Sentinel-2 images from Digital Earth Sweden's OpenEO service for a specified area of interest to the ColonyFS under **/openeo/rutvik/images**.

2. Generate cloud masks for all images in **/openeo/rutvik/images**, along with a CSV file (**cloud_coverage.csv**) containing cloud coverage percentages. Both the cloud masks and CSV file will be stored in the directory **/openeo/rutvik/cloud**.

3. Compute the NDVI average for all images in **/openeo/rutvik/images** where the cloud coverage (obtained from **/openeo/rutvik/cloud/cloud_coverage.csv**) exceeds a specified threshold. A time series plot (**ndvi_time_series.png**) and a corresponding CSV file (**ndvi_time_series.csv**) will be saved in **/openeo/rutvik/ndvi**.

4. Email the **ndvi_time_series.png** and **ndvi_time_series.csv** files to a selected user.

The selected area will be in northern Sweden, close to Luleå.

<img src="rutvik.png">

# Run the workflow
Type the following command to run the workflow:

```bash
colonies workflow submit --spec workflow.json
```

Note that the final step requires a valid Google SMTP account and will fail without one. We will explain how to create such an account later in this guide.  Additionally, ensure that executornames are updated to match an existing executor."

<img src="workflow.png">

Once the workflow is complete, the selected user will receive an email containing the NDVI time series plot and a CSV file.

<img src="mail.png">

# Technical Explanation
ColonyOS is a novel type of operating system, designed to function across a distributed architecture where its underlying components can span a geographically dispersed compute continuum.

ColonyOS is a new kind of operating system, despite being distributed where underlying components could potentially be spread across a geographically dispersed *compute continuum*. In a traditional operating system, applications are typically stored on a filesystem, like a hard drive. Similarly, in ColonyOS, we will store applications, such as Python scripts, on ColonyFS and start them just as we would with a conventional operating system.

<img src="arch.png">



