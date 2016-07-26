#!/usr/bin/python
# -*- coding: utf-8 -*-

import scipy as sp
import scipy.linalg as spla
import itertools as it
import functools as fn

class RVM(object):
    u"""
    relevance vector machine
    PRML 7.2.1を参考にした
    """

    def __init__(self,
                 kernel=lambda x, y: sp.exp(-sp.square(spla.norm(x-y))/0.05)):
        self._kernel = kernel

    def learn(self, X, t, tol=0.01, amax=1e10):
        u"""学習"""

        N = X.shape[0]
        a = sp.ones(N+1) # hyperparameter
        b = 1.0
        phi = sp.ones((N, N+1)) # design matrix
        phi[:,1:] = [[self._kernel(xi, xj) for xj in X] for xi in X]

        diff = 1
        while diff >= tol:
            sigma = spla.inv(sp.diag(a) + b * sp.dot(phi.T, phi))
            m = b * sp.dot(sigma, sp.dot(phi.T, t))
            gamma = sp.ones(N+1) - a * sigma.diagonal()
            anew = gamma / (m * m)
            bnew = (N -  gamma.sum()) / sp.square(spla.norm(t - sp.dot(phi, m)))
            anew[anew >= amax] = amax
            adiff, bdiff = anew - a, bnew - b
            diff = (adiff * adiff).sum() + bdiff * bdiff
            a, b = anew, bnew
            print ".",

        self._a = a
        self._b = b
        self._X = X
        self._m = m
        self._sigma = sigma
        self._amax = amax

    def mean(self, x):
        u"""The average of the predicted value"""

        ret = 0
        phi = sp.append([1.0], [self._kernel(x, xi) for xi in X])
        for i in range(len(self._m)):
            if self._a[i] < self._amax:
                ret += self._m[i] * phi[i]
        return ret

    def variance(self, x):
        u"""Variance of the predicted value"""

        phi = sp.append([1.0], [self._kernel(x, xi) for xi in X])
        return 1.0/self._b + sp.dot(phi.T, sp.dot(self._sigma, phi))

    def _get_a(self):
        return self._a
    # 超パラメータ
    a = property(_get_a)

    def _get_rv_index(self):
        return self._a[1:] < self._amax
    # 関連ベクトルのインデックス
    rv_index = property(_get_rv_index)


if __name__ == '__main__':
    # めんどうなのでデータはここに;-p
    data = sp.array([
        [0.000000, 0.349486],
        [0.111111, 0.830839],
        [0.222222, 1.007332],
        [0.333333, 0.971507],
        [0.444444, 0.133066],
        [0.555556, 0.166823],
        [0.666667, -0.848307],
        [0.777778, -0.445686],
        [0.888889, -0.563567],
        [1.000000, 0.261502],
        ])

    X = data[:, 0]
    t = data[:, 1]
    rvm = RVM()
    rvm.learn(X, t)

    print "a=", rvm.a

    # 描画
    import matplotlib.pyplot as plt
    x = sp.linspace(0, 1, 50)

    # +-標準偏差1つ分の幅の表示
    meshx, meshy = sp.meshgrid(sp.linspace(0, 1, 200), sp.linspace(-1.5, 1.5, 200))
    meshz = [[abs(rvm.mean(meshx[j][i]) - meshy[j][i]) <= sp.sqrt(rvm.variance(meshx[j][i]))
              for i in range(len(meshx[0]))] for j in range(len(meshx))]
    plt.contour(meshx, meshy, meshz, 1)
    plt.spring()

    # 入力
    plt.scatter(X, t, label="input")

    # 関連ベクトルの描画
    plt.scatter(X[rvm.rv_index], t[rvm.rv_index], marker='d', color='r', label="relevance vector")

    # 元の曲線を表示
    y = sp.sin(2*sp.pi*x)
    plt.plot(x, y, label="sin(2pix)")

    # RVMの予測の平均
    y_  = [rvm.mean(xi) for xi in x]
    plt.plot(x, y_, label="RVM regression")

    # 表示範囲の調整
    plt.xlim(-0.05, 1.05)
    plt.ylim(-1.5, 1.5)

    # label表示
    plt.legend()
    plt.show()