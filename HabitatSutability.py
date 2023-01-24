'''
Author: Timothy Schragel
Date: 11/29/2022
Description: Tree sutability analysis
                Uses a DEM, rainfall, summer temp, and winter temp raster to produce a habitat area layer
'''

#set up workspace   
ws = r"R:\GEOG491_591_12249_FALL2022\Student_Data\timmys\PythonFinalv2\Data"                  ##!! CHANGE FILEPATH !!##
outws = r"R:\GEOG491_591_12249_FALL2022\Student_Data\timmys\PythonFinalv2\Output"        ##!! CHANGE FILEPATH !!##
import arcpy
from arcpy.sa import *
arcpy.env.workspace = ws
arcpy.env.overwriteOutput = True


##### FUNCTIONS #####

def clipRaster(inraster, area):
    #Clip Rasters is used to clip a raster file to the study area
    newClip = arcpy.management.Clip(inraster, area, f'Clip{inraster}')
    return (newClip)

def rasterCheck(inRaster, minn, maxx):
    #check input raster for values between min and max
    # if one value is blank only use filled value
    if minn == "":
        outRaster =  Raster(inRaster) < int(maxx)
        return(outRaster)
    elif maxx == "":
        outRaster = Raster(inRaster) > int(minn)
        return(outRaster)
    else:
        x =  Raster(inRaster) < int(maxx)
        y = Raster(inRaster) > int(minn)
        return(x & y)

def minMaxCheck (inraster):
    #Ask user for minimum and maximum values, return raster with values between min and max
    try:
        minimum = arcpy.management.GetRasterProperties(inraster, 'MINIMUM')
        maximum = arcpy.management.GetRasterProperties(inraster, 'MAXIMUM')
    except Exception:
         minimum = "NA"
         maximum = "NA"
    minVal = input(f"Input minimum value for {inraster}, range of {minimum} to {maximum}: ")
    maxVal = input(f"Input maximum value for {inraster}, range of {minimum} to {maximum}: ")
    return(rasterCheck(inraster, minVal, maxVal))

def analysisAreaCheck(inputArea):
    #Check wich study area was selected and return polygon limits
    if inputArea == '1':
        return("711388.17 584312.16 992855.62 1156748.05")
    else:
        return("400000.00 145000.00 2000000.00 1375000.00")

def useLayer(inputFC):
    #Just asks if a raster is being used, this function is a bit extra NGL
    return(input(f"Are you using {inputFC}? [Y/N]"))

def dataCleanup():
    #Get rid of all created datasets in Data Folder
    arcpy.env.workspace = ws
    rasterlist = arcpy.ListRasters()

    for raster in rasterlist:
        if raster[:4].lower() == "clip":
            arcpy.Delete_management(raster)
    return()

def cleanOutput():
    #when called go to output folder, clear it, and return to ws
    arcpy.env.workspace = outws
    rasterCleanup = arcpy.ListRasters()
    for raster in rasterCleanup:
        arcpy.Delete_management(raster)
    arcpy.env.workspace = ws
    return()



def turnAllToRaster():
    #Go through data folder and turn all datasets to raster before checking what rasters the user wants to use
    print("Converting to raster...")

    # Feature Class
    fcList = arcpy.ListFeatureClasses()
    for fc in fcList:
        arcpy.conversion.FeatureToRaster(fc, field, f"fcOut{fc}")
    return()

###   MAIN   ###

def main():
    ### User Prompts ###
    analysisArea = input('Enter [1] for the Wilamette National Forest or [2] for Oregon: ')
    analysisSelection = input("Enter [1] for Douglas-Fir Habitat Analysis or [2] for custom values: ")

    ### Variables ###
    DFrasters =  ['ordemfeet','202101tMean.tif','202107tMean.tif','RainfallIN.tif']
    area = analysisAreaCheck(analysisArea)
    rasterlist = arcpy.ListRasters()
    
    
    ### Clean output folder ###
    cleanOutput()

    ### RUN PRESET ANALYSIS ###
    if analysisSelection == '1':

        # Clip datasets to study area
        for raster in rasterlist:
            if raster in DFrasters:
                clipRaster(raster, area)


        #check each layer for the proper criteria
        elevation = rasterCheck('clipordemfeet', 0, 5000)                           # 0-5000 Ft
        januaryTemperature = rasterCheck('Clip202101tMean.tif', '', 6)  #   -6 Deg F
        julyTemperature = rasterCheck("Clip202107tMean.tif", 20, 30)  #20-30 Deg F
        rain = rasterCheck('ClipRainfallIN.tif', 24, 700)                               #24-700 IN precipitation


        #switch to output folder and save habitat layer
        arcpy.env.workspace = outws
        Habitats = elevation & januaryTemperature & julyTemperature & rain
        Habitats.save('Habitat')

        #Check to see if user wants to save the other files produced. 
        save = input("Save all files [Y/N]: ")
        if save.upper() == "Y":
            elevation.save('elevation')
            rain.save('rain')
            januaryTemperature.save("janTemp")
            julyTemperature.save("julyTemp")


    #RUN CUSTOM ANALYSIS
    if analysisSelection == '2':

        # Create a list for used layers
        usedForAnalysis = []


        '''
        ### Here is the start of the feature class analysis section###
        ### While not finished the plan is to ask the user whether or not to use a fc layer,
                          as well as what field should be used ###
        ### From there it will be converted to a raster and min max values would be added later ###

        
        turnAllToRaster()
        '''

        # go through raster list and find if layer is used and if so find the min and max values
        for raster in rasterlist:
            if useLayer(raster).upper() == 'Y':
                MinMax = minMaxCheck(raster)
                usedForAnalysis.append(MinMax)
            else:
                print("Raster Skipped")

        #save output raster
        outRaster = Raster(usedForAnalysis[0]) & Raster(usedForAnalysis[1])
        i = 2
        for i in range(len(usedForAnalysis)):
            outRaster = outRaster & usedForAnalysis[i]
        arcpy.env.workspace = outws
        outRaster.save("OutRaster")

        #prompt user to save all data layers or not
        keepData = input("Do you want to keep all data layers? [Y/N]: ")
        if keepData.upper() == "Y":
            i  = 0
            for i in range(len(usedForAnalysis)):
                x = usedForAnalysis[i]
                x.save(f"{x}")
                


    # get rid of all the cliped data layers
    dataCleanup()
    print("Done.")
    return()





##### Call for Main #####
    
if __name__ == "__main__":
    main()
