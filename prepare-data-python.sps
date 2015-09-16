begin program.
import spss
import spssaux

for index, id in enumerate(spssaux.GetVariableNamesList()):
    if not id.startswith("tt"):
        # NOTE: Background question IDs starts with "tt"
        # It could be better to check IDs against survey.json
        # This might help http://stackoverflow.com/a/4028943
        if spss.GetVariableMeasurementLevel(index) != "scale":
            spss.Submit("VARIABLE LEVEL {0} (SCALE)".format(id))

end program.
