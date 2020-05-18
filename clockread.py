import cv2
import numpy as np
import math

cv2.namedWindow('Kep')

image = ['faliora.jpg', 'faliora2.jpg', 'faliora4_zaj.jpg', 'faliora7.jpg', 'faliora8.jpg', 'faliora9_zaj.jpg']

print('A program mukodese:\nA csuszkan allitsa be a kivant kepet,\nmajd nyomja meg az Enter billentyut\na szamitas elvegzesehez.\nAz eredmenyt a program a konzolra irja ki.\n')
print('A programbol valo kilepeshez nyomja meg a q billentyut!\n')

def kepbetolt(kep):
    src = cv2.imread(image[kep], cv2.IMREAD_COLOR)
    return src


cv2.createTrackbar('kep', 'Kep', 0, 5, kepbetolt)


while(True):

    key = cv2.waitKey(100)

    if key == -1:
        continue

    if key == ord('\r'):
        cv2.imshow('Kep', kepbetolt(cv2.getTrackbarPos('kep', 'Kep')))
        src = cv2.medianBlur(kepbetolt(cv2.getTrackbarPos('kep', 'Kep')), 5)

        #***********A kontraszt megnövelése a pontosabb kördetekció érdekében*********************
        lab = cv2.cvtColor(src, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        clahe = cv2.createCLAHE(clipLimit=15.0, tileGridSize=(5, 5))
        cl = clahe.apply(l)

        limg = cv2.merge((cl, a, b))

        final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        grey = cv2.cvtColor(final, cv2.COLOR_BGR2GRAY)

        rows = grey.shape[0]

        circles = cv2.HoughCircles(grey, cv2.HOUGH_GRADIENT, 1, rows / 1,
                                   param1=250, param2=25,
                                   minRadius=50, maxRadius=500)

        center = (0, 0)
        radius = 0

        #***************Az ora körvonalanak megkeresese*************************************

        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                center = (i[0], i[1])
                cv2.circle(src, center, 1, (255, 0, 0), 3)
                radius = i[2]
                cv2.circle(src, center, radius, (0, 0, 255), 3)

        #**********Az ora 'kiteritese'*******************************************************

        polar = cv2.warpPolar(src, (0, 0), center, radius, cv2.WARP_POLAR_LINEAR)
        (h, w) = polar.shape[:2]
        polar_center = (w / 2, h / 2)
        M = cv2.getRotationMatrix2D(polar_center, 180, 1.0)
        polar = cv2.warpAffine(polar, M, (w, h))
        polar = cv2.resize(polar, None, fx=2.0, fy=1.0, interpolation=cv2.INTER_LINEAR)

        #**********A kiteritett kepen elvegzem az inverz binaris kuszobolest******************

        ret, polar = cv2.threshold(polar, 120, 255, cv2.THRESH_BINARY)

        struct = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        polar = cv2.dilate(polar, struct, None, None, 1)
        polar = cv2.cvtColor(polar, cv2.COLOR_BGR2GRAY)

        ret2, polar = cv2.threshold(polar, 100, 255, cv2.THRESH_BINARY_INV)

        struct2 = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 3))
        polar = cv2.dilate(polar, struct2, None, None, 1)
        polar = cv2.erode(polar, struct, None, None, 1)

        #***********************Megkeresem a kontúrokat a binaris kepen***********************************

        contours, hierarchy = cv2.findContours(polar, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        x = [0] * 40
        y = [0] * 40
        width = [0] * 40
        height = [0] * 40

        for i in range(0, len(contours)):
            x[i], y[i], width[i], height[i] = cv2.boundingRect(contours[i])
            cv2.rectangle(polar, (x[i], y[i]), (x[i] + width[i], y[i] + height[i]), (255, 255, 255))


        #************Mergkeresem a két legkisebb x érteket(a nagyon kicsiken kívül)************************

        perc = ora = 0
        first = second = 100000
        for i in range(0, 40):
            if x[i] < 30:
                break
            else:
                #Ha az aktuális elem kisebb, mint a first, akkor mindkettőt frissítem
                if x[i] < first:
                    second = first
                    first = x[i]

                #Ha az aktuális elem a first és second között van, akkor csak a second értékét frissítem
                elif x[i] < second and x[i] != first:
                    second = x[i]


        for i in range(0, 40):
            if x[i] == second:
                ora = y[i]
            elif x[i] == first:
                perc = y[i]+(height[i]/1.5)

        #**************Kiszamolom a pont y koordinátájából az idot*************************************
        actualOra = 15-(ora/(h/12))
        actualPerc = 15-(perc/(h/60))


        #Lefele kerekíto fuggveny
        def round_down(n, decimals=0):
            multiplier = 10 ** decimals
            return math.floor(n * multiplier) / multiplier


        actualOra = round_down(actualOra, 0)
        actualPerc = round(actualPerc, 0)

        actualOra = int(actualOra)
        actualPerc = int(actualPerc)


        if 15 >= actualOra > 12:
            actualOra -= 12

        if 0 > actualPerc:
            actualPerc = abs(actualPerc)

        if actualPerc == 0:
            actualPerc = abs(actualPerc)

        print("Ido:", actualOra, ":", actualPerc, '\n')

    if key == ord('q'):
        break

cv2.destroyAllWindows()

