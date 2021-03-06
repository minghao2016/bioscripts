import subprocess as sp
import copy
import matplotlib.pyplot as plt

logFile = 'create_gabar.log'
outFile = 'models_hybrid_4COF4tnv'
modelNum = 64

orange = '#f69855'
blue = '#3a81ba'
grey = '#666666'


def md_plot(outFile, x, y, xlab, ylab, labe, fontsize=12):

    fig, ax = plt.subplots()

    ax.plot_euclidean(x, y[0], c='#f69855', marker='o', ls='', label=labe[0])
    ax.plot_euclidean(x, y[1], c='#3a81ba', marker='o', ls='', label=labe[1])
 
   #ax.locator_params(nbins=20)
    ax.set_xlabel(xlab, fontsize=fontsize)
    ax.set_ylabel(ylab, fontsize=fontsize)
   #ax.set_xlim([0, 120])
    ax.set_ylim([0.75, 1.02])

    handles, labels = ax.get_legend_handles_labels()
    lgd = ax.legend(handles, labels, loc='upper left', bbox_to_anchor=(1, 1.025))
    ax.grid('on')

    fig.set_size_inches(7.5, 5)
    fig.savefig(outFile, dpi=300, bbox_extra_artists=(lgd,), bbox_inches='tight' )

def md_table(title, data):

    print('------------------------------------------------')
    print(title)
    print('------------------------------------------------')
    print('model    molpdf      DOPE')   
    for line in data:
        print('{0:5d}\t{1:7.0f}\t{2:9.0f}'.format(*line))
    print('------------------------------------------------')

# read mark table from log into list of lists
modelList = [ model.split() for model in sp.check_output([ 'grep', 'Summary of successfully produced models:', logFile, '-A', str(modelNum+2) ]).decode('utf-8').split('\n')[3:-1] ]

# format each list of log
modelList = [ [ int(model[0][19:21]), float(model[1]), float(model[2]) ] for model in modelList ]

# finds best models
bestMolPDF = copy.deepcopy(min(modelList, key=lambda x: x[1]))
bestDOPE = copy.deepcopy(min(modelList, key=lambda x: x[2]))
print('Best molpdf: {}'.format(bestMolPDF))
print('Best DOPE: {}'.format(bestDOPE))

listByMOLPDF = sorted(modelList, key=lambda x: x[1])
listByDOPE = sorted(modelList, key=lambda x: x[2])

md_table('Best 25% by molpdf', listByMOLPDF[0:15])
md_table('Best 25% by DOPE', listByDOPE[0:15])

listBest = []
for model in listByMOLPDF[0:15]:
    if model in listByDOPE[0:15]:
        listBest.append(model)
listBestbyMOLPDF = sorted(listBest, key=lambda x: x[1])
md_table('Best common by molpdf', listBestbyMOLPDF)

# normalization (closer to one - better)
for model in modelList:
    model[1] = bestMolPDF[1]/model[1]
    model[2] = model[2]/bestDOPE[2]

# plots all models normalized (closer to one - better)
toPlot = list(zip(*modelList))
md_plot(outFile, toPlot[0], toPlot[1:3], 'model', 'quality relative to best', ['molpdf', 'dope'])
