begin program.
import spss, spssaux
for index, id in enumerate(spssaux.GetVariableNamesList()):
   if spss.GetVariableMeasurementLevel(index) != "scale":
      spss.Submit("VARIABLE LEVEL {0} (SCALE)".format(id))
end program.
