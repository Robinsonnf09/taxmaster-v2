// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title RegistroPrecatorios
 * @dev Smart Contract para registro imutável de cessões de precatórios
 * @notice Compatível com Ethereum, Polygon, Binance Smart Chain
 */
contract RegistroPrecatorios {
    
    struct Cessao {
        string numeroPrecatorio;
        address cedente;
        address cessionario;
        uint256 valorCessao;
        uint256 timestamp;
        string hashDocumento;  // SHA-256 do documento de cessão
        bool ativa;
    }
    
    // Mapeamento de ID da cessão => dados da cessão
    mapping(uint256 => Cessao) public cessoes;
    
    // Contador de cessões
    uint256 public totalCessoes;
    
    // Controle de acesso
    address public admin;
    mapping(address => bool) public registradores;
    
    // Eventos
    event CessaoRegistrada(
        uint256 indexed cessaoId,
        string numeroPrecatorio,
        address indexed cedente,
        address indexed cessionario,
        uint256 valorCessao
    );
    
    event CessaoRevogada(uint256 indexed cessaoId);
    
    modifier onlyAdmin() {
        require(msg.sender == admin, "Apenas admin");
        _;
    }
    
    modifier onlyRegistrador() {
        require(registradores[msg.sender] || msg.sender == admin, "Sem permissao");
        _;
    }
    
    constructor() {
        admin = msg.sender;
        registradores[msg.sender] = true;
    }
    
    /**
     * @dev Registra nova cessão de precatório
     * @param _numeroPrecatorio Número do ofício/precatório
     * @param _cedente Endereço do cedente original
     * @param _cessionario Endereço do cessionário (comprador)
     * @param _valorCessao Valor da cessão em centavos (ex: 50000000 = R$ 500.000,00)
     * @param _hashDocumento Hash SHA-256 do documento de cessão
     */
    function registrarCessao(
        string memory _numeroPrecatorio,
        address _cedente,
        address _cessionario,
        uint256 _valorCessao,
        string memory _hashDocumento
    ) public onlyRegistrador returns (uint256) {
        require(_cedente != address(0), "Cedente invalido");
        require(_cessionario != address(0), "Cessionario invalido");
        require(_valorCessao > 0, "Valor deve ser maior que zero");
        require(bytes(_hashDocumento).length == 64, "Hash invalido");
        
        totalCessoes++;
        
        cessoes[totalCessoes] = Cessao({
            numeroPrecatorio: _numeroPrecatorio,
            cedente: _cedente,
            cessionario: _cessionario,
            valorCessao: _valorCessao,
            timestamp: block.timestamp,
            hashDocumento: _hashDocumento,
            ativa: true
        });
        
        emit CessaoRegistrada(
            totalCessoes,
            _numeroPrecatorio,
            _cedente,
            _cessionario,
            _valorCessao
        );
        
        return totalCessoes;
    }
    
    /**
     * @dev Consulta dados de uma cessão
     */
    function consultarCessao(uint256 _cessaoId) public view returns (
        string memory numeroPrecatorio,
        address cedente,
        address cessionario,
        uint256 valorCessao,
        uint256 timestamp,
        string memory hashDocumento,
        bool ativa
    ) {
        require(_cessaoId > 0 && _cessaoId <= totalCessoes, "Cessao inexistente");
        
        Cessao memory c = cessoes[_cessaoId];
        return (
            c.numeroPrecatorio,
            c.cedente,
            c.cessionario,
            c.valorCessao,
            c.timestamp,
            c.hashDocumento,
            c.ativa
        );
    }
    
    /**
     * @dev Revoga cessão (apenas admin)
     */
    function revogarCessao(uint256 _cessaoId) public onlyAdmin {
        require(_cessaoId > 0 && _cessaoId <= totalCessoes, "Cessao inexistente");
        require(cessoes[_cessaoId].ativa, "Cessao ja revogada");
        
        cessoes[_cessaoId].ativa = false;
        
        emit CessaoRevogada(_cessaoId);
    }
    
    /**
     * @dev Adiciona registrador autorizado
     */
    function adicionarRegistrador(address _registrador) public onlyAdmin {
        registradores[_registrador] = true;
    }
    
    /**
     * @dev Remove registrador
     */
    function removerRegistrador(address _registrador) public onlyAdmin {
        registradores[_registrador] = false;
    }
    
    /**
     * @dev Verifica autenticidade de documento
     */
    function verificarDocumento(string memory _hashDocumento) public view returns (
        bool existe,
        uint256[] memory cessaoIds
    ) {
        uint256[] memory ids = new uint256[](totalCessoes);
        uint256 contador = 0;
        
        for (uint256 i = 1; i <= totalCessoes; i++) {
            if (keccak256(bytes(cessoes[i].hashDocumento)) == keccak256(bytes(_hashDocumento))) {
                ids[contador] = i;
                contador++;
            }
        }
        
        // Redimensiona array
        uint256[] memory resultado = new uint256[](contador);
        for (uint256 i = 0; i < contador; i++) {
            resultado[i] = ids[i];
        }
        
        return (contador > 0, resultado);
    }
}