const service = require('./public/js/api/processos-mock-service.js');

console.log('\n╔════════════════════════════════════════╗');
console.log('║   TESTANDO SERVIÇO MOCK REALISTA      ║');
console.log('╚════════════════════════════════════════╝\n');

// Estatísticas
const stats = service.getEstatisticas();
console.log('📊 ESTATÍSTICAS:');
console.log(`   Total de processos: ${stats.total}`);
console.log(`   Valor total: R$ ${stats.valorTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`);

console.log('\n🏛️ POR TRIBUNAL:');
Object.entries(stats.porTribunal).forEach(([tribunal, dados]) => {
    console.log(`   ${tribunal}: ${dados.quantidade} processos - R$ ${dados.valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`);
});

console.log('\n📋 POR STATUS:');
Object.entries(stats.porStatus).forEach(([status, dados]) => {
    console.log(`   ${status}: ${dados.quantidade} processos`);
});

console.log('\n🔍 EXEMPLO DE PROCESSO:');
const processos = service.buscarTodos();
const exemplo = processos[0];
console.log(`   Número: ${exemplo.numero}`);
console.log(`   Tribunal: ${exemplo.tribunal}`);
console.log(`   Credor: ${exemplo.credor}`);
console.log(`   Valor: R$ ${exemplo.valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`);
console.log(`   Status: ${exemplo.status}`);
console.log(`   Movimentações: ${exemplo.movimentacoes.length}`);

console.log('\n✅ Serviço funcionando perfeitamente!\n');
