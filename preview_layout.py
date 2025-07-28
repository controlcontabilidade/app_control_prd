#!/usr/bin/env python3
"""
Script para testar o layout modernizado dos indicadores
"""

# Simular dados para teste visual
dados_exemplo = """
<div class="row mt-4 mb-4">
    <div class="col-12">
        <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-0 pb-0">
                <h5 class="mb-0 text-muted">
                    <i class="bi bi-speedometer2 me-2"></i>
                    Indicadores do Sistema
                </h5>
            </div>
            <div class="card-body pt-3">
                <!-- Indicadores Principais em linha -->
                <div class="row g-3 mb-3">
                    <div class="col-lg-3 col-md-6">
                        <div class="d-flex align-items-center p-3 rounded-3" style="background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6;">
                            <div class="flex-shrink-0 me-3">
                                <div class="rounded-circle d-flex align-items-center justify-content-center" style="width: 45px; height: 45px; background: #3b82f6;">
                                    <i class="bi bi-people text-white fs-5"></i>
                                </div>
                            </div>
                            <div class="flex-grow-1">
                                <h4 class="mb-0 fw-bold text-primary">5</h4>
                                <small class="text-muted">Total de Clientes</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-3 col-md-6">
                        <div class="d-flex align-items-center p-3 rounded-3" style="background: rgba(34, 197, 94, 0.1); border-left: 4px solid #22c55e;">
                            <div class="flex-shrink-0 me-3">
                                <div class="rounded-circle d-flex align-items-center justify-content-center" style="width: 45px; height: 45px; background: #22c55e;">
                                    <i class="bi bi-check-circle text-white fs-5"></i>
                                </div>
                            </div>
                            <div class="flex-grow-1">
                                <h4 class="mb-0 fw-bold text-success">5</h4>
                                <small class="text-muted">Clientes Ativos</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-3 col-md-6">
                        <div class="d-flex align-items-center p-3 rounded-3" style="background: rgba(245, 158, 11, 0.1); border-left: 4px solid #f59e0b;">
                            <div class="flex-shrink-0 me-3">
                                <div class="rounded-circle d-flex align-items-center justify-content-center" style="width: 45px; height: 45px; background: #f59e0b;">
                                    <i class="bi bi-building text-white fs-6"></i>
                                </div>
                            </div>
                            <div class="flex-grow-1">
                                <h4 class="mb-0 fw-bold" style="color: #f59e0b;">0</h4>
                                <small class="text-muted">Empresas</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-3 col-md-6">
                        <div class="d-flex align-items-center p-3 rounded-3" style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444;">
                            <div class="flex-shrink-0 me-3">
                                <div class="rounded-circle d-flex align-items-center justify-content-center" style="width: 45px; height: 45px; background: #ef4444;">
                                    <i class="bi bi-house text-white fs-6"></i>
                                </div>
                            </div>
                            <div class="flex-grow-1">
                                <h4 class="mb-0 fw-bold" style="color: #ef4444;">1</h4>
                                <small class="text-muted">Domésticas</small>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Regime Tributário e Serviços em duas colunas -->
                <div class="row g-3">
                    <!-- Coluna 1: Regime Tributário -->
                    <div class="col-md-6">
                        <div class="card border-0" style="background: #f8fafc;">
                            <div class="card-body p-3">
                                <h6 class="mb-3 text-muted fw-semibold">
                                    <i class="bi bi-pie-chart me-2"></i>REGIME TRIBUTÁRIO
                                </h6>
                                <div class="row g-2">
                                    <div class="col-6">
                                        <div class="text-center p-2 rounded-3" style="background: rgba(99, 102, 241, 0.1);">
                                            <div class="d-flex align-items-center justify-content-center mb-1">
                                                <i class="bi bi-person-badge me-2" style="color: #6366f1;"></i>
                                                <span class="fw-bold h6 mb-0" style="color: #6366f1;">1</span>
                                            </div>
                                            <small class="text-muted">MEI</small>
                                        </div>
                                    </div>
                                    <div class="col-6">
                                        <div class="text-center p-2 rounded-3" style="background: rgba(34, 197, 94, 0.1);">
                                            <div class="d-flex align-items-center justify-content-center mb-1">
                                                <i class="bi bi-graph-up me-2" style="color: #22c55e;"></i>
                                                <span class="fw-bold h6 mb-0" style="color: #22c55e;">1</span>
                                            </div>
                                            <small class="text-muted">Simples</small>
                                        </div>
                                    </div>
                                    <div class="col-6">
                                        <div class="text-center p-2 rounded-3" style="background: rgba(245, 158, 11, 0.1);">
                                            <div class="d-flex align-items-center justify-content-center mb-1">
                                                <i class="bi bi-calculator me-2" style="color: #f59e0b;"></i>
                                                <span class="fw-bold h6 mb-0" style="color: #f59e0b;">1</span>
                                            </div>
                                            <small class="text-muted">Presumido</small>
                                        </div>
                                    </div>
                                    <div class="col-6">
                                        <div class="text-center p-2 rounded-3" style="background: rgba(168, 85, 247, 0.1);">
                                            <div class="d-flex align-items-center justify-content-center mb-1">
                                                <i class="bi bi-cash-stack me-2" style="color: #a855f7;"></i>
                                                <span class="fw-bold h6 mb-0" style="color: #a855f7;">1</span>
                                            </div>
                                            <small class="text-muted">Real</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Coluna 2: Serviços -->
                    <div class="col-md-6">
                        <div class="card border-0" style="background: #f8fafc;">
                            <div class="card-body p-3">
                                <h6 class="mb-3 text-muted fw-semibold">
                                    <i class="bi bi-briefcase me-2"></i>SERVIÇOS PRESTADOS
                                </h6>
                                <div class="d-flex flex-column gap-2">
                                    <div class="d-flex align-items-center justify-content-between p-2 rounded-3" style="background: white; border: 1px solid rgba(59, 130, 246, 0.2);">
                                        <div class="d-flex align-items-center">
                                            <i class="bi bi-calculator me-2 text-primary"></i>
                                            <small class="text-muted">Contábil</small>
                                        </div>
                                        <span class="badge bg-primary">3</span>
                                    </div>
                                    <div class="d-flex align-items-center justify-content-between p-2 rounded-3" style="background: white; border: 1px solid rgba(34, 197, 94, 0.2);">
                                        <div class="d-flex align-items-center">
                                            <i class="bi bi-file-text me-2 text-success"></i>
                                            <small class="text-muted">Fiscal</small>
                                        </div>
                                        <span class="badge bg-success">3</span>
                                    </div>
                                    <div class="d-flex align-items-center justify-content-between p-2 rounded-3" style="background: white; border: 1px solid rgba(245, 158, 11, 0.2);">
                                        <div class="d-flex align-items-center">
                                            <i class="bi bi-people me-2" style="color: #f59e0b;"></i>
                                            <small class="text-muted">Pessoal</small>
                                        </div>
                                        <span class="badge" style="background: #f59e0b;">3</span>
                                    </div>
                                    <div class="d-flex align-items-center justify-content-between p-2 rounded-3" style="background: white; border: 1px solid rgba(168, 85, 247, 0.2);">
                                        <div class="d-flex align-items-center">
                                            <i class="bi bi-briefcase me-2" style="color: #a855f7;"></i>
                                            <small class="text-muted">BPO</small>
                                        </div>
                                        <span class="badge" style="background: #a855f7;">1</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
"""

print("📊 Layout modernizado dos indicadores criado!")
print("✨ Características:")
print("   - Mais compacto e ocupa menos espaço")
print("   - Layout em duas colunas para regime e serviços")
print("   - Design mais limpo e moderno")
print("   - Cores mais suaves e elegantes")
print("   - Melhor aproveitamento do espaço horizontal")
