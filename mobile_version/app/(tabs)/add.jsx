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
  Switch
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { useFocusEffect } from 'expo-router';
import DateTimePicker from '@react-native-community/datetimepicker'; 
import { ConfigAPI } from '../../api/config_api';
import { PeopleAPI } from '../../api/people_api';

export default function AddPersonScreen() {
  // --- ESTADOS DEL FORMULARIO ---
  const [form, setForm] = useState({
    first_name: '', last_name: '', email: '', birthdate: '2000-01-01',
    gender: 'Masculino', dni: '', phone_number: '', marital_status: '',
    membership_status: '', social_security: '', street: '', neighborhood: '',
    house_number: '', consolidation_id: '', cdb: '', baptized: false,
    trusted_person_info: ''
  });

  // --- ESTADOS PARA EL CALENDARIO DESPLEGABLE ---
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [currentDate, setCurrentDate] = useState(new Date(2000, 0, 1)); 

  // --- ESTADOS PARA LOS DROPDOWNS GENERALES ---
  const [dropdowns, setDropdowns] = useState({
    ministries: [],     
    consolidations: [],  
    cdbs: [],  
    maritalStatuses: [],  
    membershipStatuses: [],  
    occupations: []
  });
  
  // Selectores temporales para los Pickers de la UI
  const [currentMinistrySelection, setCurrentMinistrySelection] = useState('');
  const [currentAreaSelection, setCurrentAreaSelection] = useState('');
  const [filteredAreas, setFilteredAreas] = useState([]);
  
  // LISTAS MULTI-SELECCIÓN (ESTADO INTERNO DINÁMICO)
  const [selectedMinistries, setSelectedMinistries] = useState([]); // [{ ministry_id, ministry_name, area_id, area_name }]
  const [selectedOccupations, setSelectedOccupations] = useState([]); // [{ id, name }]

  const [currentOccSelection, setCurrentOccSelection] = useState('');
  const [loadingConfig, setLoadingConfig] = useState(true);
  const [loadingAreas, setLoadingAreas] = useState(false); 
  const [submitting, setSubmitting] = useState(false);

  // --- CARGAR CONFIGURACIÓN INICIAL ---
  const loadInitialConfig = async () => {
    try {
      setLoadingConfig(true);
      const [minis, cons, cdbs, maritals, memberships, occs] = await Promise.all([
        ConfigAPI.getAllMinistries(),
        ConfigAPI.getAllConsolidations(),
        ConfigAPI.getAllCdbOptions(), 
        ConfigAPI.getMaritalStatuses(),
        ConfigAPI.getMembershipStatuses(),
        ConfigAPI.getAllOccupations()
      ]);

      setDropdowns({
        ministries: minis || [],
        consolidations: cons || [],
        cdbs: cdbs || [],
        maritalStatuses: maritals || [],
        membershipStatuses: memberships || [],
        occupations: occs || []
      });

      const defaultMinistry = minis?.[0]?.ministry_id || '';
      const defaultCons = cons?.[0]?.id || cons?.[0]?.consolidation_id || '';
      const defaultCdb = cdbs?.[0]?.id || cdbs?.[0]?.cdb_id || '';
      const defaultMarital = maritals?.[0]?.name || '';
      const defaultMember = memberships?.[0]?.name || '';

      setForm(prev => ({
        ...prev,
        consolidation_id: defaultCons.toString(),
        cdb: defaultCdb.toString(),
        marital_status: defaultMarital,
        membership_status: defaultMember
      }));

      if (defaultMinistry) {
        setCurrentMinistrySelection(defaultMinistry.toString());
        fetchAreasForMinistry(defaultMinistry);
      }

      if (occs && occs.length > 0) {
        const firstId = occs[0]?.id || occs[0]?.occupation_id;
        setCurrentOccSelection(firstId ? firstId.toString() : '');
      }

    } catch (error) {
      console.error("Error cargando catálogos de configuración:", error);
      Alert.alert("Error", "No se pudieron sincronizar los selectores.");
    } finally {
      setLoadingConfig(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      loadInitialConfig();
    }, [])
  );

  const fetchAreasForMinistry = async (ministryId) => {
    try {
      setLoadingAreas(true);
      const areas = await ConfigAPI.getAreasByMinistry(parseInt(ministryId, 10));
      setFilteredAreas(areas || []);
      // Inicializa en vacío para que la opción por defecto sea "[ Ninguna ]"
      setCurrentAreaSelection(''); 
    } catch (error) {
      console.error("Error buscando áreas para ministerio:", error);
      setFilteredAreas([]);
      setCurrentAreaSelection('');
    } finally {
      setLoadingAreas(false);
    }
  };

  const handleMinistryChange = (ministryId) => {
    setCurrentMinistrySelection(ministryId);
    fetchAreasForMinistry(ministryId); 
  };

  const handleInputChange = (key, value) => {
    setForm(prev => ({ ...prev, [key]: value }));
  };

  const onDateChange = (event, selectedDate) => {
    setShowDatePicker(false); 
    if (selectedDate) {
      setCurrentDate(selectedDate);
      const year = selectedDate.getFullYear();
      const month = String(selectedDate.getMonth() + 1).padStart(2, '0');
      const day = String(selectedDate.getDate()).padStart(2, '0');
      handleInputChange('birthdate', `${year}-${month}-${day}`);
    }
  };

  // --- LÓGICA MULTI-MINISTERIO CORREGIDA ---
  const addMinistryRelation = () => {
    if (!currentMinistrySelection) return;

    const ministryFound = dropdowns.ministries.find(
      m => m.ministry_id.toString() === currentMinistrySelection.toString()
    );
    
    // Si currentAreaSelection está vacío, significa que eligió "[ Ninguna ]"
    const areaFound = currentAreaSelection 
      ? filteredAreas.find(a => a.area_id.toString() === currentAreaSelection.toString())
      : null;

    if (ministryFound) {
      // Evitamos duplicar la misma combinación exacta de Ministerio y Área
      const isDuplicate = selectedMinistries.some(
        m => m.ministry_id === ministryFound.ministry_id && m.area_id === (areaFound?.area_id || null)
      );

      if (isDuplicate) {
        Alert.alert("Aviso", "Esta combinación de ministerio y área ya fue añadida.");
        return;
      }

      setSelectedMinistries([
        ...selectedMinistries,
        {
          ministry_id: ministryFound.ministry_id,
          ministry_name: ministryFound.name,
          area_id: areaFound ? areaFound.area_id : null,
          area_name: areaFound ? areaFound.area : '[Sin Área]'
        }
      ]);
    }
  };

  const removeMinistryRelation = (index) => {
    setSelectedMinistries(selectedMinistries.filter((_, i) => i !== index));
  };

  // --- LÓGICA MULTI-OCUPACIÓN ---
  const addOccupation = () => {
    if (!currentOccSelection) return;
    const found = dropdowns.occupations.find(o => (o.id || o.occupation_id).toString() === currentOccSelection.toString());
    if (found) {
      const id = found.id || found.occupation_id;
      if (selectedOccupations.some(o => o.id === id)) return;
      setSelectedOccupations([...selectedOccupations, { id, name: found.name }]);
    }
  };

  const removeOccupation = (id) => {
    setSelectedOccupations(selectedOccupations.filter(o => o.id !== id));
  };

  // --- ENVIAR FORMULARIO CORREGIDO ---
  const onSubmit = async () => {
    if (!form.first_name.trim() || !form.last_name.trim()) {
      Alert.alert("Error", "Nombre y Apellido son campos obligatorios.");
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        ...form,
        baptized: !!form.baptized,
        dni: form.dni ? parseInt(form.dni, 10) : null,
        house_number: form.house_number ? parseInt(form.house_number, 10) : null,
        consolidation_id: form.consolidation_id ? parseInt(form.consolidation_id, 10) : null,
        cdb: form.cdb ? parseInt(form.cdb, 10) : null,
        
        // ENVIAMOS LAS ARREGLOS DE SELECCIÓN MULTIPLE CONVERTIDOS A ENTEROS
        ministry_ids: selectedMinistries.map(m => parseInt(m.ministry_id, 10)),
        area_ids: selectedMinistries.filter(m => m.area_id !== null).map(m => parseInt(m.area_id, 10)),
        occupation_ids: selectedOccupations.map(o => parseInt(o.id, 10))
      };

      Object.keys(payload).forEach(key => {
        if (payload[key] === "" || payload[key] === null || payload[key] === undefined) {
          delete payload[key];
        }
      });

      await PeopleAPI.createPerson(payload);
      Alert.alert("Éxito 🎉", "Persona creada exitosamente en Renuevo.");
      clearForm();
    } catch (error) {
      console.error("Error al guardar persona:", error.message);
      Alert.alert("Error 422 / Servidor", "Hubo un problema al validar el formulario contra el servidor.");
    } finally {
      setSubmitting(false);
    }
  };

  const clearForm = () => {
    setForm({
      first_name: '', last_name: '', email: '', birthdate: '2000-01-01',
      gender: 'Masculino', dni: '', phone_number: '', 
      marital_status: dropdowns.maritalStatuses[0]?.name || '',
      membership_status: dropdowns.membershipStatuses[0]?.name || '', 
      social_security: '', street: '', neighborhood: '', house_number: '', 
      consolidation_id: (dropdowns.consolidations[0]?.id || dropdowns.consolidations[0]?.consolidation_id || '').toString(), 
      cdb: (dropdowns.cdbs[0]?.id || dropdowns.cdbs[0]?.cdb_id || '').toString(), 
      baptized: false, trusted_person_info: ''
    });
    setCurrentDate(new Date(2000, 0, 1));
    setSelectedOccupations([]);
    setSelectedMinistries([]);
    if (dropdowns.ministries[0]?.ministry_id) {
      handleMinistryChange(dropdowns.ministries[0].ministry_id);
    }
  };

  if (loadingConfig) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#7A4A97" />
        <Text style={{ marginTop: 10, color: '#5A5A5A' }}>Sincronizando con Renuevo Church...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scrollContent}>
      <Text style={styles.sectionHeader}>⛪ Nueva Persona</Text>

      {/* --- SECCIÓN 1: DATOS PERSONALES --- */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Datos Identificatorios</Text>
        <Text style={styles.label}>Nombre *</Text>
        <TextInput style={styles.input} value={form.first_name} onChangeText={(v) => handleInputChange('first_name', v)} placeholder="Ej: Josías" />
        
        <Text style={styles.label}>Apellido *</Text>
        <TextInput style={styles.input} value={form.last_name} onChangeText={(v) => handleInputChange('last_name', v)} placeholder="Ej: Pérez" />
        
        <Text style={styles.label}>DNI</Text>
        <TextInput style={styles.input} keyboardType="numeric" value={form.dni} onChangeText={(v) => handleInputChange('dni', v)} placeholder="Solo números" />
        
        <Text style={styles.label}>Género</Text>
        <View style={styles.pickerContainer}>
          <Picker selectedValue={form.gender} onValueChange={(v) => handleInputChange('gender', v)}>
            <Picker.Item label="Masculino" value="Masculino" />
            <Picker.Item label="Femenino" value="Femenino" />
          </Picker>
        </View>
        
        <Text style={styles.label}>Fecha de Nacimiento</Text>
        <TouchableOpacity style={styles.dateSelectorButton} onPress={() => setShowDatePicker(true)}>
          <Text style={styles.dateSelectorText}>
            {form.birthdate ? form.birthdate : "Seleccionar Fecha"} 📅
          </Text>
        </TouchableOpacity>

        {showDatePicker && (
          <DateTimePicker
            value={currentDate}
            mode="date"
            display="calendar"
            onChange={onDateChange}
            maximumDate={new Date()}
          />
        )}
      </View>

      {/* --- SECCIÓN MULTI-MINISTERIO CON ÁREA OPCIONAL REPARADA --- */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Asignación de Ministerios</Text>

        <Text style={styles.label}>Seleccionar Ministerio</Text>
        <View style={styles.pickerContainer}>
          <Picker 
            selectedValue={currentMinistrySelection} 
            onValueChange={(itemValue) => handleMinistryChange(itemValue)}
          >
            {dropdowns.ministries.map((m) => (
              <Picker.Item key={m.ministry_id} label={m.name} value={m.ministry_id.toString()} />
            ))}
          </Picker>
        </View>

        <Text style={styles.label}>Seleccionar Área Específica</Text>
        <View style={styles.pickerContainer}>
          {loadingAreas ? (
            <ActivityIndicator size="small" color="#7A4A97" style={{ paddingVertical: 14 }} />
          ) : (
            <Picker 
              selectedValue={currentAreaSelection} 
              onValueChange={(itemValue) => setCurrentAreaSelection(itemValue)}
            >
              {filteredAreas.length === 0 ? (
                <Picker.Item label="[ Sin áreas en este ministerio ]" value="" />
              ) : (
                [
                  { area_id: '', area: '[ Ninguna - Solo Ministerio ]' },
                  ...filteredAreas
                ].map((a, index) => (
                  <Picker.Item 
                    key={a.area_id ? a.area_id.toString() : `empty-${index}`} 
                    label={a.area} 
                    value={a.area_id ? a.area_id.toString() : ''} 
                  />
                ))
              )}
            </Picker>
          )}
        </View>

        <TouchableOpacity style={[styles.addButtonInline, { marginTop: 12 }]} onPress={addMinistryRelation}>
          <Text style={styles.btnText}>+ Vincular Ministerio y Área</Text>
        </TouchableOpacity>

        {/* Listado dinámico en pantalla de ministerios agregados */}
        {selectedMinistries.map((min, index) => (
          <View key={index} style={styles.itemRow}>
            <Text style={styles.itemText}>💥 {min.ministry_name} → <Text style={{fontWeight: 'bold'}}>{min.area_name}</Text></Text>
            <TouchableOpacity onPress={() => removeMinistryRelation(index)}>
              <Text style={styles.deleteText}>Quitar</Text>
            </TouchableOpacity>
          </View>
        ))}
      </View>

      {/* --- SECCIÓN 2: CONTACTO Y DOMICILIO --- */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Contacto y Ubicación</Text>
        <Text style={styles.label}>Teléfono</Text>
        <TextInput style={styles.input} keyboardType="phone-pad" value={form.phone_number} onChangeText={(v) => handleInputChange('phone_number', v)} />
        <Text style={styles.label}>Correo Electrónico</Text>
        <TextInput style={styles.input} keyboardType="email-address" autoCapitalize="none" value={form.email} onChangeText={(v) => handleInputChange('email', v)} />
        <Text style={styles.label}>Calle</Text>
        <TextInput style={styles.input} value={form.street} onChangeText={(v) => handleInputChange('street', v)} />
        <Text style={styles.label}>Barrio</Text>
        <TextInput style={styles.input} value={form.neighborhood} onChangeText={(v) => handleInputChange('neighborhood', v)} />
        <Text style={styles.label}>Número de casa</Text>
        <TextInput style={styles.input} keyboardType="numeric" value={form.house_number} onChangeText={(v) => handleInputChange('house_number', v)} />
      </View>

      {/* --- SECCIÓN 3: IGLESIA Y MEMBRESÍA --- */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Información Eclesiástica</Text>
        <View style={styles.switchRow}>
          <Text style={styles.labelBold}>¿Está Bautizado?</Text>
          <Switch value={form.baptized} onValueChange={(v) => handleInputChange('baptized', v)} trackColor={{ true: '#7A4A97' }} />
        </View>
        <Text style={styles.label}>Estado Civil</Text>
        <View style={styles.pickerContainer}>
          <Picker selectedValue={form.marital_status} onValueChange={(v) => handleInputChange('marital_status', v)}>
            {dropdowns.maritalStatuses.map((m, i) => <Picker.Item key={i} label={m.name} value={m.name} />)}
          </Picker>
        </View>
        <Text style={styles.label}>Estado de Membresía</Text>
        <View style={styles.pickerContainer}>
          <Picker selectedValue={form.membership_status} onValueChange={(v) => handleInputChange('membership_status', v)}>
            {dropdowns.membershipStatuses.map((m, i) => <Picker.Item key={i} label={m.name} value={m.name} />)}
          </Picker>
        </View>
        <Text style={styles.label}>Nivel de Consolidación</Text>
        <View style={styles.pickerContainer}>
          <Picker selectedValue={form.consolidation_id} onValueChange={(v) => handleInputChange('consolidation_id', v)}>
            {dropdowns.consolidations.map((c, i) => (
              <Picker.Item key={i} label={c.level || c.name} value={(c.id || c.consolidation_id).toString()} />
            ))}
          </Picker>
        </View>
        <Text style={styles.label}>¿CDB?</Text>
        <View style={styles.pickerContainer}>
          <Picker selectedValue={form.cdb} onValueChange={(v) => handleInputChange('cdb', v)}>
            {dropdowns.cdbs.map((cd, i) => (
              <Picker.Item key={i} label={cd.number?.toString() || cd.name} value={(cd.id || cd.cdb_id).toString()} />
            ))}
          </Picker>
        </View>
      </View>

      {/* --- SECCIÓN 4: OCUPACIONES --- */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Ocupaciones / Oficios</Text>
        <View style={styles.row}>
          <View style={[styles.pickerContainer, { flex: 1, marginRight: 10 }]}>
            <Picker selectedValue={currentOccSelection} onValueChange={(itemValue) => setCurrentOccSelection(itemValue)}>
              {dropdowns.occupations.map((o, i) => (
                <Picker.Item key={i} label={o.name} value={(o.id || o.occupation_id).toString()} />
              ))}
            </Picker>
          </View>
          <TouchableOpacity style={styles.smallButton} onPress={addOccupation}>
            <Text style={styles.btnText}>Agregar</Text>
          </TouchableOpacity>
        </View>
        {selectedOccupations.map((occ) => (
          <View key={occ.id} style={styles.itemRow}>
            <Text style={styles.itemText}>• {occ.name}</Text>
            <TouchableOpacity onPress={() => removeOccupation(occ.id)}>
              <Text style={styles.deleteText}>Quitar</Text>
            </TouchableOpacity>
          </View>
        ))}
      </View>

      {/* --- SECCIÓN 5: EMERGENCY --- */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Contacto de Emergencia</Text>
        <TextInput 
          style={[styles.input, { height: 80, textAlignVertical: 'top' }]} 
          multiline numberOfLines={4} 
          value={form.trusted_person_info} 
          onChangeText={(v) => handleInputChange('trusted_person_info', v)} 
          placeholder="Nombre completo y teléfono de contacto..." 
        />
      </View>

      {/* --- BOTÓN GUARDAR PRINCIPAL --- */}
      <TouchableOpacity style={styles.submitButton} onPress={onSubmit} disabled={submitting}>
        {submitting ? <ActivityIndicator color="#FFF" /> : <Text style={styles.submitBtnText}>Agregar Persona</Text>}
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F0E6F6' },
  scrollContent: { padding: 15, paddingBottom: 40 },
  sectionHeader: { fontSize: 22, fontWeight: 'bold', color: '#7A4A97', textAlign: 'center', marginVertical: 15 },
  card: { backgroundColor: '#FFF', borderRadius: 12, padding: 16, marginBottom: 15, elevation: 2, borderWidth: 1, borderColor: '#E2E8F0' },
  cardTitle: { fontSize: 16, fontWeight: 'bold', color: '#7A4A97', marginBottom: 12, borderBottomWidth: 1, borderBottomColor: '#F0E6F6', paddingBottom: 4 },
  label: { fontSize: 14, color: '#5A5A5A', marginBottom: 4, marginTop: 8 },
  labelBold: { fontSize: 15, fontWeight: '600', color: '#5A5A5A' },
  input: { backgroundColor: '#FFFBF5', borderWidth: 1, borderColor: '#DDD', borderRadius: 6, paddingHorizontal: 12, paddingVertical: 8, fontSize: 15, color: '#333' },
  pickerContainer: { backgroundColor: '#FFFBF5', borderWidth: 1, borderColor: '#DDD', borderRadius: 6, justifyContent: 'center' },
  switchRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginVertical: 8 },
  row: { flexDirection: 'row', alignItems: 'center', marginTop: 5, marginBottom: 10 },
  smallButton: { backgroundColor: '#7A4A97', paddingVertical: 12, paddingHorizontal: 18, borderRadius: 6, justifyContent: 'center' },
  addButtonInline: { backgroundColor: '#7A4A97', paddingVertical: 10, borderRadius: 6, alignItems: 'center' },
  btnText: { color: '#FFF', fontWeight: 'bold' },
  itemRow: { flexDirection: 'row', justifyContent: 'space-between', backgroundColor: '#F5F5F7', padding: 10, borderRadius: 6, marginVertical: 4, alignItems: 'center' },
  itemText: { fontSize: 14, color: '#333', flex: 1 },
  deleteText: { color: '#c0392b', fontWeight: 'bold', marginLeft: 10 },
  submitButton: { backgroundColor: '#7A4A97', padding: 15, borderRadius: 8, alignItems: 'center', marginTop: 10, elevation: 3 },
  submitBtnText: { color: '#FFF', fontSize: 16, fontWeight: 'bold' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F0E6F6' },
  dateSelectorButton: { backgroundColor: '#FFFBF5', borderWidth: 1, borderColor: '#DDD', borderRadius: 6, paddingHorizontal: 12, paddingVertical: 12, justifyContent: 'center' },
  dateSelectorText: { fontSize: 15, color: '#333' }
});