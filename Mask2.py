import cv2
import pytesseract
import re

path= 'img2.jpeg'
img = cv2.imread(path,cv2.COLOR_BGR2RGB)
img_h,img_w,_ = img.shape
area_of_img = img_h,img_w

cv2.imshow('result',img)
cv2.waitKey(0)
# To mask adharId present bellow
rect = cv2.rectangle(img, (int(img_w*.30), int(img_h*.88)), (int(img_w*.55), int(img_h*.91)), (255, 255, 255), -1)
cv2.imshow('img_mask',img)
cv2.waitKey(0)

gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

# perform gaussian blur to smoothen image
blur = cv2.GaussianBlur(gray, (5, 5), 0)

# threshold the image using Otsus method to preprocess for tesseract
ret, thresh = cv2.threshold(gray, 12 , 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
# create rectangular kernel for dilation
rect_kern = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
# apply dilation to make regions more clear
dilation = cv2.dilate(thresh, rect_kern, iterations=3)
# find contours of regions of interest within license plate
contours, hierarchy = cv2.findContours(dilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)




##### SHOW THE IMAGES FOR VISUAL INSPECTION ####
cv2.imshow("Gray", gray)
cv2.waitKey(0)
cv2.imshow("Otsu Threshold", thresh)
cv2.waitKey(0)
cv2.imshow("Dilation", dilation)
cv2.waitKey(0)


# sort contours left-to-right
sorted_contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])
# create copy of gray image
im2 = gray.copy()
# create blank string to hold license plate number
id_num = ""
# loop through contours and find individual letters and numbers in license plate
for i,cnt in enumerate(sorted_contours):
    x, y, w, h = cv2.boundingRect(cnt)
    height, width = im2.shape


    area = h * w

    if area < 10*30: continue
    if x/(y+0.0001) <  1/4 : continue
    if y < 0.55 *img_h : continue
    if y > 0.65*img_h : continue

    # draw the rectangle
    if x > 0.6 * img_w:
        #rect = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 0)
        pass
    else:
        rect = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), -1)
    # grab character region of image
    lp_buff = 0
    roi = thresh[y - lp_buff:y + h + lp_buff, x - lp_buff:x + w + lp_buff]
    # perfrom bitwise not to flip image to black text on white background
    roi = cv2.bitwise_not(roi)
    # perform another blur on character region
    roi = cv2.medianBlur(roi, 5)

    try:
        text = pytesseract.image_to_string(roi,
                                           config='-c tessedit_char_whitelist=0123456789 --psm 8 --oem 3')

        '''
        psm stands for page segmentation mode --psm 8 means treat the image as a single mode
        (psm moodes available are many ranging from 0 upto 13)
        Page segmentation modes:
          0    Orientation and script detection (OSD) only.
          1    Automatic page segmentation with OSD.
          2    Automatic page segmentation, but no OSD, or OCR.
          3    Fully automatic page segmentation, but no OSD. (Default)
          4    Assume a single column of text of variable sizes.
          5    Assume a single uniform block of vertically aligned text.
          6    Assume a single uniform block of text.
          7    Treat the image as a single text line.
          8    Treat the image as a single word.
          9    Treat the image as a single word in a circle.
         10    Treat the image as a single character.
         11    Sparse text. Find as much text as possible in no particular order.
         12    Sparse text with OSD.
         13    Raw line. Treat the image as a single text line,bypassing hacks that are Tesseract-specific.
        --oem ocr engine mode 3 means use default mode which is avilable
        '''

        # clean tesseract text by removing any unwanted blank spaces
        clean_text = re.sub('[\W_]+', '', text)
        id_num += clean_text

        cv2.imshow("Character's Segmented", img)
        cv2.waitKey(0)
        # Put the detected Number on image
        id_print = cv2.putText(img, text[:4], (x, y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.5, (0, 255, 0), 2)
        cv2.imshow("Id_Print", id_print)
        cv2.waitKey(0)
    except:
        print('pytesseract fails ')
        text = None
img_mask = 'img2_mask_wo_id.jpeg'
cv2.imwrite(img_mask, img)
print('Unique Id on Adharcard ',id_num)