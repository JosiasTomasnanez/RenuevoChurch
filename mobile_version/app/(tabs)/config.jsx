import React, { useState, useCallback } from 'react'; 
import { 
  View, 
  Text, 
  TextInput, 
  ScrollView, 
  TouchableOpacity, 
  StyleSheet, 
  Alert, 
  ActivityIndicator,
  FlatList
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { useFocusEffect } from 'expo-router'; 
import { ConfigAPI } from '../../api/config_api'; 

// Las 7 pestañas horizontales completas
const TABS = [
  { id: 'ministries', label: 'Ministerios' },
  { id: 'areas', label: 'Áreas' },
  { id: 'consolidation', label: 'Consolidación' },
  { id: 'cdb', label: 'CDB' },
  { id: 'marital_statuses', label: 'Estado Civil' },
  { id: 'membership_statuses', label: 'Membresía' },
  { id: 'occupations', label: 'Ocupaciones' }
];

export default function ConfigScreen() {
  const [activeTab, setActiveTab] = useState('ministries');
  const [loading, setLoading] = useState(false);
  const [inputText, setInputText] = useState('');
  
  // Todos los catálogos del servidor sincronizados
  const [data, setData] = useState({
    ministries: [],
    consolidations: [],
    cdbs: [],
    marital_statuses: [],
    membership_statuses: [],
    occupations: []
  });

  // Estados para manejar las Áreas relacionales
  const [selectedMinistryId, setSelectedMinistryId] = useState('');
  const [filteredAreas, setFilteredAreas] = useState([]);

  // --- CARGA INICIAL DESDE EL SERVIDOR ---
  const loadData = async () => {
    try {
      setLoading(true);
      const [minis, consolidations, cdbs, maritals, memberships, occs] = await Promise.all([
        ConfigAPI.getAllMinistries(),
        ConfigAPI.getAllConsolidations(),
        ConfigAPI.getAllCdbOptions(),
        ConfigAPI.getMaritalStatuses(),
        ConfigAPI.getMembershipStatuses(),
        ConfigAPI.getAllOccupations()
      ]);

      setData({
        ministries: minis || [],
        consolidations: consolidations || [],
        cdbs: cdbs || [],
        marital_statuses: maritals || [],
        membership_statuses: memberships || [],
        occupations: occs || []
      });

      if (minis && minis.length > 0 && !selectedMinistryId) {
        setSelectedMinistryId((minis[0].ministry_id || minis[0].id).toString());
      }
    } catch (error) {
      console.error("Error cargando configuración:", error);
      Alert.alert("Error", "No se pudieron sincronizar los datos de configuración.");
    } finally {
      setLoading(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      loadData();
    }, [selectedMinistryId])
  );

  // --- ESCUCHA CAMBIOS DE MINISTERIO EN LA PESTAÑA ÁREAS ---
  React.useEffect(() => {
    if (activeTab === 'areas' && selectedMinistryId) {
      fetchAreasForMinistry(selectedMinistryId);
    }
  }, [selectedMinistryId, activeTab]);

  const fetchAreasForMinistry = async (ministryId) => {
    try {
      setLoading(true);
      const areas = await ConfigAPI.getAreasByMinistry(parseInt(ministryId, 10));
      setFilteredAreas(areas || []);
    } catch (error) {
      console.error("Error buscando áreas:", error);
      setFilteredAreas([]);
    } finally {
      setLoading(false);
    }
  };

  // --- AGREGAR REGISTRO (ALTA) ---
  const handleAddItem = async () => {
    const value = inputText.trim();
    if (!value && activeTab !== 'areas') {
      Alert.alert("Error", "El campo no puede estar vacío.");
      return;
    }

    try {
      setLoading(true);
      switch (activeTab) {
        case 'ministries':
          await ConfigAPI.createMinistry({ name: value });
          break;
        case 'areas':
          if (!selectedMinistryId) return Alert.alert("Error", "Selecciona un ministerio padre.");
          if (!value) return Alert.alert("Error", "Ingresa el nombre del área.");
          await ConfigAPI.createArea(parseInt(selectedMinistryId, 10), value);
          break;
        case 'consolidation':
          await ConfigAPI.createConsolidation({ level: value });
          break;
        case 'cdb':
          // Envía el string directo sin 'parseInt' para que acepte letras
          await ConfigAPI.createCdb({ number: value }); 
          break;
        case 'marital_statuses':
          await ConfigAPI.createMaritalStatus({ name: value });
          break;
        case 'membership_statuses':
          await ConfigAPI.createMembershipStatus({ name: value });
          break;
        case 'occupations':
          await ConfigAPI.createOccupation({ name: value });
          break;
      }
      
      setInputText('');
      Alert.alert("Éxito 🎉", "Registro agregado correctamente.");
      
      if (activeTab === 'areas') {
        fetchAreasForMinistry(selectedMinistryId);
      } else {
        loadData();
      }
    } catch (error) {
      console.error("Error al guardar:", error);
      Alert.alert("Error", "No se pudo guardar el registro en el servidor.");
    } finally {
      setLoading(false);
    }
  };

  // --- ELIMINAR REGISTRO (BAJA) ---
  const handleDeleteItem = async (id) => {
    Alert.alert(
      "Confirmar eliminación",
      "¿Estás seguro de que deseas eliminar este elemento?",
      [
        { text: "Cancelar", style: "cancel" },
        { 
          text: "Eliminar", 
          style: "destructive", 
          onPress: async () => {
            try {
              setLoading(true);
              switch (activeTab) {
                case 'ministries': await ConfigAPI.deleteMinistry(id); break;
                case 'areas': await ConfigAPI.deleteArea(id); break;
                case 'consolidation': await ConfigAPI.deleteConsolidation(id); break;
                case 'cdb': await ConfigAPI.deleteCdb(id); break;
                case 'marital_statuses': await ConfigAPI.deleteMaritalStatus(id); break;
                case 'membership_statuses': await ConfigAPI.deleteMembershipStatus(id); break;
                case 'occupations': await ConfigAPI.deleteOccupation(id); break;
              }
              
              if (activeTab === 'areas') {
                fetchAreasForMinistry(selectedMinistryId);
              } else {
                loadData();
              }
            } catch (error) {
              console.error("Error al eliminar:", error);
              Alert.alert("Error", "No se pudo eliminar el registro seleccionado.");
            } finally {
              setLoading(false);
            }
          }
        }
      ]
    );
  };

  // --- RENDERS DE FILAS Y DATA ---
  const renderItemRow = ({ item }) => {
    let displayName = "";
    let itemId = null;

    if (activeTab === 'ministries') { 
      displayName = item.name; 
      itemId = item.ministry_id || item.id; 
    }
    else if (activeTab === 'areas') { 
      displayName = item.area || item.name; 
      itemId = item.area_id || item.id; 
    }
    else if (activeTab === 'consolidation') { 
      displayName = item.level || item.name; 
      itemId = item.consolidation_id || item.id; 
    }
    else if (activeTab === 'cdb') { 
      displayName = item.number?.toString().includes('CDB') ? item.number : `CDB N° ${item.number}`; 
      itemId = item.cdb_id || item.id; 
    }
    else if (activeTab === 'marital_statuses') { 
      displayName = item.name; 
      // Multi-búsqueda preventiva para evitar valores "undefined"
      itemId = item.marital_status_id || item.id || item.status_id; 
    }
    else if (activeTab === 'membership_statuses') { 
      displayName = item.name; 
      // Multi-búsqueda preventiva para evitar valores "undefined"
      itemId = item.membership_status_id || item.id || item.status_id; 
    }
    else if (activeTab === 'occupations') { 
      displayName = item.name; 
      itemId = item.occupation_id || item.id; 
    }

    // Validación estricta antes de renderizar el botón
    const isIdValid = itemId !== null && itemId !== undefined && itemId !== "undefined" && itemId !== "";

    return (
      <View style={styles.itemRow}>
        <Text style={styles.itemText}>{displayName}</Text>
        {isIdValid ? (
          <TouchableOpacity style={styles.deleteButton} onPress={() => handleDeleteItem(itemId)}>
            <Text style={styles.deleteButtonText}>Eliminar</Text>
          </TouchableOpacity>
        ) : (
          <Text style={{ fontSize: 11, color: '#999', fontStyle: 'italic' }}>[ID No Sincronizado]</Text>
        )}
      </View>
    );
  };

  const getCurrentListData = () => {
    if (activeTab === 'ministries') return data.ministries;
    if (activeTab === 'areas') return filteredAreas;
    if (activeTab === 'consolidation') return data.consolidations;
    if (activeTab === 'cdb') return data.cdbs;
    if (activeTab === 'marital_statuses') return data.marital_statuses;
    if (activeTab === 'membership_statuses') return data.membership_statuses;
    if (activeTab === 'occupations') return data.occupations;
    return [];
  };

  return (
    <View style={styles.container}>
      {/* Botonera Horizontal */}
      <View style={{ height: 50 }}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.tabsContainer}>
          {TABS.map((tab) => (
            <TouchableOpacity 
              key={tab.id} 
              style={[styles.tabButton, activeTab === tab.id && styles.activeTabButton]}
              onPress={() => { setActiveTab(tab.id); setInputText(''); }}
            >
              <Text style={[styles.tabButtonText, activeTab === tab.id && styles.activeTabButtonText]}>
                {tab.label}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Tarjeta de Entrada de Datos */}
      <View style={styles.card}>
        {activeTab === 'areas' && (
          <View style={{ marginBottom: 12 }}>
            <Text style={styles.label}>Seleccionar Ministerio Padre:</Text>
            <View style={styles.pickerContainer}>
              <Picker 
                selectedValue={selectedMinistryId} 
                onValueChange={(itemValue) => setSelectedMinistryId(itemValue)}
              >
                {data.ministries.map((m) => {
                  const mId = m.ministry_id || m.id;
                  return (
                    <Picker.Item key={mId} label={m.name} value={mId.toString()} />
                  );
                })}
              </Picker>
            </View>
          </View>
        )}

        <Text style={styles.label}>
          {activeTab === 'cdb' ? 'Identificador o Número del CDB:' : 'Nombre del Registro:'}
        </Text>
        
        <View style={styles.inputRow}>
          <TextInput 
            style={styles.input} 
            value={inputText} 
            onChangeText={setInputText}
            placeholder={activeTab === 'cdb' ? "Ej: 105, 12B o Norte" : "Ej: Soltero, Miembro Activo..."}
            keyboardType="default" 
          />
          <TouchableOpacity style={styles.addButton} onPress={handleAddItem} disabled={loading}>
            <Text style={styles.addButtonText}>Agregar</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Listado de Elementos del Servidor */}
      <Text style={styles.sectionTitle}>Registros cargados en el Servidor</Text>
      {loading ? (
        <ActivityIndicator size="large" color="#7A4A97" style={{ marginTop: 20 }} />
      ) : (
        <FlatList
          data={getCurrentListData()}
          keyExtractor={(item, index) => index.toString()}
          renderItem={renderItemRow}
          contentContainerStyle={{ paddingBottom: 20 }}
          ListEmptyComponent={
            <Text style={styles.emptyText}>No hay registros cargados para esta categoría.</Text>
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F0E6F6', padding: 15 },
  tabsContainer: { flexDirection: 'row', paddingBottom: 10 },
  tabButton: { backgroundColor: '#E2E8F0', paddingHorizontal: 16, paddingVertical: 8, borderRadius: 20, marginRight: 8, height: 38 },
  activeTabButton: { backgroundColor: '#7A4A97' },
  tabButtonText: { color: '#4A5568', fontWeight: '600' },
  activeTabButtonText: { color: '#FFF' },
  card: { backgroundColor: '#FFF', borderRadius: 12, padding: 16, marginBottom: 15, elevation: 2, borderWidth: 1, borderColor: '#E2E8F0' },
  label: { fontSize: 14, color: '#5A5A5A', marginBottom: 6, fontWeight: '600' },
  pickerContainer: { backgroundColor: '#FFFBF5', borderWidth: 1, borderColor: '#DDD', borderRadius: 6, justifyContent: 'center' },
  inputRow: { flexDirection: 'row', alignItems: 'center', marginTop: 5 },
  input: { flex: 1, backgroundColor: '#FFFBF5', borderWidth: 1, borderColor: '#DDD', borderRadius: 6, paddingHorizontal: 12, paddingVertical: 8, fontSize: 15, marginRight: 8, color: '#333' },
  addButton: { backgroundColor: '#7A4A97', paddingVertical: 10, paddingHorizontal: 16, borderRadius: 6 },
  addButtonText: { color: '#FFF', fontWeight: 'bold' },
  sectionTitle: { fontSize: 15, fontWeight: 'bold', color: '#5A5A5A', marginBottom: 10 },
  itemRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#FFF', padding: 12, borderRadius: 8, marginBottom: 8, elevation: 1, borderWidth: 1, borderColor: '#E2E8F0' },
  itemText: { fontSize: 15, color: '#333', fontWeight: '500' },
  deleteButton: { backgroundColor: '#FFF', borderWidth: 1, borderColor: '#c0392b', paddingVertical: 6, paddingHorizontal: 12, borderRadius: 6 },
  deleteButtonText: { color: '#c0392b', fontWeight: 'bold', fontSize: 12 },
  emptyText: { textAlign: 'center', color: '#777', marginTop: 20, fontSize: 14 }
});