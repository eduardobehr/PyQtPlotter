# PyQtPlotter
A simple plotter based on pyqtgraph and PyQt5

# How to use
## Analytic explicit f(X) function plot
After launching, the user is prompted to write an expression f(X) and specify the range and number of sample points.
Note that the independent variable X *must be uppercase*, otherwise it will not work.
When the button Plot is pressed, it draws the given curve in blue. Each draw call cycles through seven colors.
When pressing the Reset button, the plot area is cleared and the color reset to the first.

## CSV data points plot
This program also features a mode to plot CSV files.
The CSV file must have the first column as independent variable (e.g. time t, X, etc) and all the other columns will be plotted as individual curves as function of the first column.
As an example, the CSV file should be of the following text format:

```python
Time (s),Vds (V),Ids (A),Vrg1 (V),Vgs (V)
0.0,0.0,-72.0,-0.4,14.4
1.0,4.0,-68.0,-0.4,14.8
2.0,4.0,-68.0,-0.8,14.8
```

Aditional functionality may be used while right-clicking in the plot area, although not officially supported yet.
