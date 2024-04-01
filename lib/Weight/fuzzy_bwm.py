import pandas as pd
import requests
import openpyxl
import warnings
import json
import sys
warnings.filterwarnings('ignore')

pd.options.mode.chained_assignment = None  # default='warn'

if __name__ == '__main__':
    input_path = sys.argv[1]; output_path = sys.argv[2]
    address=input_path

    df=pd.read_excel(address, sheet_name = "Sheet1", skiprows = 2,  nrows= 9, usecols=[1,2,3],header=None)
    df.columns=["Criteria","Best","Worst"]
    # print(df)

    Best = df["Criteria"][df[df['Best'] == "Equally importance"].index.tolist()[0]]
    Worst = df["Criteria"][df[df['Worst'] == "Equally importance"].index.tolist()[0]]
    df.columns = ["Criteria", Best, Worst]
    Cnum = df.shape[0]

    df.set_index(df["Criteria"], inplace=True)
    # Fuzzification
    Fuzzy = {"Equally importance": [1, 1, 1],
             "Weakly important": [2 / 3, 1, 3 / 2],
             "Fairly important": [3 / 2, 2, 5 / 2],
             "Very important": [5 / 2, 3, 7 / 2],
             "Absolutely important": [7 / 2, 4, 9 / 2]}

    for i in [Best, Worst]:
        for j in range(df.shape[0]):
            df[i][j] = Fuzzy[df[i][j]]

    weight = dict()
    # print(df)

    #=============================================================================
    # Model
    #=============================================================================
    import pyomo.environ as pyo
    Model = pyo.ConcreteModel()

    # Set
    Model.Criteria=pyo.Set(initialize=df["Criteria"])

    # Set and variable
    Model.L=pyo.Var(Model.Criteria, within=pyo.PositiveReals)
    Model.M=pyo.Var(Model.Criteria, within=pyo.PositiveReals)
    Model.U=pyo.Var(Model.Criteria, within=pyo.PositiveReals)
    Model.ksi=pyo.Var(within=pyo.NonNegativeReals)

    def obj1(model):
        return Model.ksi
    Model.obj1=pyo.Objective(expr=obj1 ,sense=pyo.minimize)
    # Model.obj1.pprint()

    L=[Model.L, Model.M, Model.U]
    Lp=L.copy(); Lp.reverse()

    def Co1(Model, i, j):
        return (j[Best]-df[Best][i][L.index(j)]*Lp[L.index(j)][i]<= Model.ksi*Lp[L.index(j)][i])
    Model.Co1 = pyo.Constraint(Model.Criteria, L, rule=Co1)
    # Model.Co1.pprint()

    def Co2(Model, i, j):
        return (j[Best]-df[Best][i][L.index(j)]*Lp[L.index(j)][i]>= -Model.ksi*Lp[L.index(j)][i])
    Model.Co2 = pyo.Constraint(Model.Criteria, L, rule=Co2)
    # Model.Co2.pprint()

    def Co3(Model, i, j):
        return (j[i]-df[Worst][i][L.index(j)]*Lp[L.index(j)][Worst]<= Model.ksi*Lp[L.index(j)][Worst])
    Model.Co3 = pyo.Constraint(Model.Criteria, L, rule=Co3)
    # Model.Co3.pprint()

    def Co4(Model, i,j):
        return (j[i]-df[Worst][i][L.index(j)]*Lp[L.index(j)][Worst]>= -Model.ksi*Lp[L.index(j)][Worst])
    Model.Co4 = pyo.Constraint(Model.Criteria, L, rule=Co4)
    # Model.Co4.pprint()

    def Co5(Model):
        return (sum(j[i] if L.index(j)!=1 else 4*j[i] for i in Model.Criteria for j in L)/6==1)
    Model.Co5 = pyo.Constraint(rule=Co5)
    # Model.Co5.pprint()

    def Co6(Model,i):
        return (Model.L[i]<=Model.M[i])
    Model.Co6 = pyo.Constraint(Model.Criteria,rule=Co6)
    # Model.Co6.pprint()

    def Co7(Model,i):
        return (Model.M[i]<=Model.U[i])
    Model.Co7 = pyo.Constraint(Model.Criteria,rule=Co7)

    import pyomo.opt as pyopt

    results = pyopt.SolverFactory("ipopt").solve(Model, tee=False)  # doctest: +SKIP

    for i in Model.Criteria:
        a = []
        for j in L:
            a.append(j[i].value)
        weight.update({i: a})

    """
    print("ksi= ",Model.ksi())
    Model.pprint()
    Model.display()
    
    """
    # print('============================================\n')
    final_w = []
    for key in weight.keys():
        temp = (weight[key][0]+4*weight[key][1]+weight[key][2])/6
        final_w.append(temp)
    #     print(key,weight[key])
    # print("ksi= ",Model.ksi())
    # print(final_w)
    # print('CR=',Model.ksi()/8.04)

    out = {}
    out.update({'weight': final_w})
    out.update({'ksi': Model.ksi()})
    out.update({'CR': Model.ksi()/8.04})
    with open(output_path, 'w') as f:
        json.dump(out, f)
    f.close()
