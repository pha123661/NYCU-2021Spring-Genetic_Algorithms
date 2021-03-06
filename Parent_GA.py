import matplotlib.pyplot as plt
import multiprocessing as mp
import random
from Child_GA_TSP import Child_GA
from load_tsp import LoadTsp


class Parent_GA():
    def __init__(self, NUM_ITERATION=10, NUM_CHROME=20, Pc=0.5, Pm=0.01):
        '''
        Field of chromosome (Value encoding)
        [Pc, Pm, NUM_CHROME]
        '''
        self.NUM_ITERATION = NUM_ITERATION
        self.NUM_CHROME = NUM_CHROME
        self.NUM_BIT = 3

        self.Pc = Pc
        self.Pm = Pm

        self.NUM_PARENT = NUM_CHROME

        # Child 參數區間設定
        self.Pc_range = [0.6, 1]
        self.Pm_range = [0, 0.01]
        self.Chrome_range = [30, 50]

        self.TSP_maps = LoadTsp()

    def initPop(self):
        pop = []
        for _ in range(self.NUM_CHROME):
            Pc = random.uniform(*self.Pc_range)
            Pm = random.uniform(*self.Pm_range)
            CHROME = random.randint(*self.Chrome_range)
            pop.append([Pc, Pm, CHROME])
        return pop

    def fitFunc(self, x):
        '''
        Definition of fitness function:
        average of iterations for each map
        '''
        Pc, Pm, chrome = x
        sum_ = 0
        for graph in self.TSP_maps:
            sum_ += float(Child_GA(Pc=Pc, Pm=Pm,
                                   NUM_CHROME=chrome, TSP_graph=graph))
        fit_value = sum_ / len(self.TSP_maps)
        return fit_value

    def evaluatePop(self, P):
        with mp.Pool(mp.cpu_count()) as pool:
            return pool.map(self.fitFunc, P)

    def selection(self, p, p_fit):
        '''
        Rank selection
        '''
        a = []
        sorted_p = [x for _, x in sorted(zip(p_fit, p), reverse=True)]
        weights = list(range(1, len(sorted_p)+1))
        for _ in range(self.NUM_PARENT):
            parent = random.choices(sorted_p, weights=weights)[0]
            a.append(parent)
        return a

    def TF(self, name):
        '''
        Returns True of False with given weight
        '''
        if name == "Pc":
            return random.choices([True, False], weights=[self.Pc, 1-self.Pc])[0]
        elif name == "Pm":
            return random.choices([True, False], weights=[self.Pm, 1-self.Pm])[0]
        else:
            raise IndexError(name, "not found")

    def crossover(self, P):
        a = []
        for p in P:
            if self.TF("Pc"):
                c = random.randrange(1, self.NUM_BIT)
                another = random.choice(P)
                child1 = p[:c]+another[c:]
                child2 = another[:c]+p[c:]
                a.append(child1)
                a.append(child2)
        return a

    def mutation(self, p):
        '''
        Uniform mutation: 
        randomly choose one genome and initialize it
        '''
        for ch in p:
            if self.TF("Pm"):
                k = random.randrange(self.NUM_BIT)
                if k == 0:   # Initialize Pc
                    ch[k] = random.uniform(*self.Pc_range)
                elif k == 1:  # Initialize Pm
                    ch[k] = random.uniform(*self.Pm_range)
                elif k == 2:  # Initialize NUM_CHROME
                    ch[k] = random.randint(*self.Chrome_range)
                else:
                    raise IndexError("Wrong mutation!")

    def replace(self, p, p_fit, a, a_fit):
        b = p + a
        b_fit = p_fit + a_fit
        ret_fit, ret = [], []
        for t, tt in sorted(zip(b_fit, b)):
            ret_fit.append(t)
            ret.append(tt)
        return ret[:self.NUM_CHROME], ret_fit[:self.NUM_CHROME]

    def Eval(self, plot=True, return_fit=False):
        pop = self.initPop()
        pop_fit = self.evaluatePop(pop)
        mean_outputs = [sum(pop_fit)/len(pop_fit)]
        best_outputs = [min(pop_fit)]
        for i in range(self.NUM_ITERATION):
            parent = self.selection(pop, pop_fit)
            offspring = self.crossover(parent)
            self.mutation(offspring)
            offspring_fit = self.evaluatePop(offspring)
            pop, pop_fit = self.replace(
                pop, pop_fit, offspring, offspring_fit)
            print("############# Iteration: ", i+1, "#############")
            for p, f in zip(pop, pop_fit):
                print(p, "  fit: ", f)
            print("Best one:\n"
                  "Pc: %s, Pm: %s, NUM_CHROME: %s" % tuple(pop[0]),
                  "fit: ", pop_fit[0])
            mean_outputs.append(sum(pop_fit)/len(pop_fit))
            best_outputs.append(min(pop_fit))
        if plot:
            plt.plot(mean_outputs)
            plt.plot(best_outputs)
            plt.legend(["mean", "best"])
            plt.xlabel("Iteration")
            plt.ylabel("Fitness")
            plt.show()
        if return_fit:
            pop_fit[0]


if __name__ == "__main__":
    a = Parent_GA(
        NUM_ITERATION=20,
        NUM_CHROME=12,
        Pc=0.8,
        Pm=0.1
    )
    a.Eval(plot=True)
