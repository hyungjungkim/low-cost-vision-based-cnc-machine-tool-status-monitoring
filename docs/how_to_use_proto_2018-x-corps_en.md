# How to use - Proto_2018-x-coprs
0. Install required libraries (please refer to the dependencies).  
1. Copy the **cnc-2018.traineddata** from the **custom_tessdata** to the **tessdata** folder in the Tesseract-OCR.  
2. Run **kem_cncmt_client_demo_app.py**. A client app is displayed.  
3. Click **Connect** in the **Camera** menu. A CNC HMI sample image screen is displayed.  
![](proto_2018-x-corps/kem_cncmt_how_to_use-1.png)
4. Press the ‘**c**’ key on the keyboard, and **drag the mouse cursor** on the image screen to select the area you want to monitor. A **threshold setting dialog** is displayed.  
![](proto_2018-x-corps/kem_cncmt_how_to_use-2.png)
5. Adjust the **threshold setting slider** to make the data more visible with the grayscale image, and press the ‘**t**’ key on the keyboard to pop up the **ROI Editor dialog**.  
![](proto_2018-x-corps/kem_cncmt_how_to_use-3.png)
![](proto_2018-x-corps/kem_cncmt_how_to_use-4.png)
6. Select the appropriate item from the **Name** dropdown list, and click the **Save** button to save the ROI data.  
![](proto_2018-x-corps/kem_cncmt_how_to_use-5.png)
7. Review the stored ROI data on the client app.  
8. Move to the **Monitoring Setup** tab, and press the **Run** button. Then, the OCR processed results for the stored ROI are monitored.  
![](proto_2018-x-corps/kem_cncmt_how_to_use-6.png)
