import React, { useState, useEffect, useCallback } from 'react';
import { 
  View, 
  Text, 
  FlatList, 
  TextInput, 
  ActivityIndicator, 
  StyleSheet, 
  SafeAreaView,
  TouchableOpacity,
  Modal,
  ScrollView
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { useFocusEffect, useRouter } from 'expo-router';
import { PeopleAPI } from '../../api/people_api';
import { ConfigAPI } from '../../api/config_api';

export default function SearchScreen() {
  // --- ESTADOS DE DATOS ---
  const [allPeople, setAllPeople] = useState<any[]>([]); 
  const [displayedPeople, setDisplayedPeople] = useState<any[]>([]); 
  const [searchQuery, setSearchQuery] = useState('');
  
  // --- ESTADOS DE CARGA ---
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [loadingFilters, setLoadingFilters] = useState(false);

  // --- SELECCIÓN EN LISTA ---
  const [expandedPersonId, setExpandedPersonId] = useState<string | null>(null);
  const [bottomViewMode, setBottomViewMode] = useState<'ministry' | 'occupation'>('ministry');
  
  // Guardamos los datos completos del perfil individual devuelto por el Backend
  const [expandedPersonData, setExpandedPersonData] = useState<any | null>(null);
  const [personDetails, setPersonDetails] = useState<{ ministries: any[], occupations: any[] }>({ ministries: [], occupations: [] });

  // --- MODAL DE FILTROS AVANZADOS ---
  const [isFilterModalOpen, setIsFilterModalOpen] = useState(false);
  
  const [filterCatalogs, setFilterCatalogs] = useState({
    ministries: [] as any[],
    occupations: [] as any[],
    consolidations: [] as any[],
    cdbs: [] as any[],
    neighborhoods: [] as string[],
    marital_statuses: [] as any[],
    membership_statuses: [] as any[],
  });

  const [activeFilters, setActiveFilters] = useState({
    ministry: '',
    occupation: '',
    marital_status: '',
    membership_status: '',
    neighborhood: '',
    gender: '',
    baptized: '',
    cdb: '',
    consolidation_id: '',
    age_range: 'todos' 
  });

  const router = useRouter();

  // --- CARGAR DATOS ---
  const loadInitialData = async (showLoadingIndicator = true) => {
    if (showLoadingIndicator) setLoading(true);
    try {
      const peopleData = await PeopleAPI.getAllPeople();
      setAllPeople(peopleData || []);

      const uniqueNeighborhoods: string[] = Array.from(
        new Set(
          peopleData
            .map((p: any) => p.address?.neighborhood || p.neighborhood)
            .filter((n: any) => n && n.trim() !== '')
        )
      ) as string[];

      const [minis, occs, cons, cdbs, maritalStatuses, membershipStatuses] = await Promise.all([
        ConfigAPI.getAllMinistries().catch(() => []),
        ConfigAPI.getAllOccupations().catch(() => []),
        ConfigAPI.getAllConsolidations().catch(() => []),
        ConfigAPI.getAllCdbOptions().catch(() => []),
        ConfigAPI.getMaritalStatuses().catch(() => []),
        ConfigAPI.getMembershipStatuses().catch(() => []),
      ]);

      setFilterCatalogs({
        ministries: minis || [],
        occupations: occs || [],
        consolidations: cons || [],
        cdbs: cdbs || [],
        neighborhoods: uniqueNeighborhoods.sort(),
        marital_statuses: maritalStatuses || [],
        membership_statuses: membershipStatuses || [],
      });

    } catch (error) {
      console.log("Error cargando índice o catálogos:", error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      loadInitialData(true);
    }, [])
  );

  // --- CALCULAR EDAD ---
  const calculateAge = (birthdateString: string) => {
    if (!birthdateString) return null;
    try {
      const birthDate = new Date(birthdateString);
      const today = new Date();
      let age = today.getFullYear() - birthDate.getFullYear();
      const monthDiff = today.getMonth() - birthDate.getMonth();
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
      }
      return age;
    } catch {
      return null;
    }
  };

  // --- PARSEO DE FECHAS HUMANO ---
  const formatBirthdate = (dateString: string) => {
    if (!dateString) return 'No registrada';
    try {
      const parts = dateString.split('-');
      if (parts.length === 3) {
        return `${parts[2]}/${parts[1]}/${parts[0]}`; 
      }
      return dateString;
    } catch {
      return dateString;
    }
  };

  // --- RESOLUTORES DE ID A TEXTO ---
  const getCdbName = (cdbValue: any) => {
    if (!cdbValue) return 'Ninguna / No pertenece';
    const match = filterCatalogs.cdbs.find(
      c => (c.id?.toString() === cdbValue.toString()) || (c.cdb_id?.toString() === cdbValue.toString())
    );
    return match ? (match.name || match.description || `CDB ${match.number || cdbValue}`) : `CDB ID: ${cdbValue}`;
  };

  const getConsolidationLevel = (consolidationValue: any) => {
    if (!consolidationValue) return 'Sin asignar';
    const match = filterCatalogs.consolidations.find(
      c => (c.id?.toString() === consolidationValue.toString()) || (c.consolidation_id?.toString() === consolidationValue.toString())
    );
    return match ? (match.level || match.name || match.description) : `Nivel ID: ${consolidationValue}`;
  };

  // --- MOTOR DE FILTRADO ---
  useEffect(() => {
    let isMounted = true;

    const applyFilters = async () => {
      let result = [...allPeople];

      if (searchQuery.trim() !== '') {
        const query = searchQuery.toLowerCase();
        result = result.filter(p => 
          (p.first_name && p.first_name.toLowerCase().includes(query)) ||
          (p.last_name && p.last_name.toLowerCase().includes(query)) ||
          (p.dni && p.dni.toString().includes(query)) ||
          (p.email && p.email.toLowerCase().includes(query))
        );
      }

      if (activeFilters.ministry) {
        try {
          const peopleByMinistry = await PeopleAPI.getPeopleByMinistry(Number(activeFilters.ministry));
          const allowedIds = new Set((peopleByMinistry || []).map((p: any) => (p.person_id || p.id)?.toString()));
          result = result.filter(p => allowedIds.has((p.person_id || p.id || '').toString()));
        } catch (error) {
          console.log('Error filtrando por ministerio:', error);
        }
      }

      if (activeFilters.occupation) {
        try {
          const peopleByOccupation = await PeopleAPI.getPeopleByOccupation(Number(activeFilters.occupation));
          const allowedIds = new Set((peopleByOccupation || []).map((p: any) => (p.person_id || p.id)?.toString()));
          result = result.filter(p => allowedIds.has((p.person_id || p.id || '').toString()));
        } catch (error) {
          console.log('Error filtrando por ocupación:', error);
        }
      }

      if (activeFilters.neighborhood) {
        result = result.filter(p => (p.address?.neighborhood || p.neighborhood) === activeFilters.neighborhood);
      }
      if (activeFilters.marital_status) {
        result = result.filter(p => p.marital_status === activeFilters.marital_status);
      }
      if (activeFilters.membership_status) {
        result = result.filter(p => p.membership_status === activeFilters.membership_status);
      }
      if (activeFilters.gender) {
        result = result.filter(p => p.gender === activeFilters.gender);
      }
      if (activeFilters.baptized) {
        const target = activeFilters.baptized === 'Sí';
        result = result.filter(p => !!p.baptized === target);
      }
      if (activeFilters.cdb) {
        result = result.filter(p => p.cdb?.toString() === activeFilters.cdb.toString());
      }
      if (activeFilters.consolidation_id) {
        result = result.filter(p => p.consolidation_id?.toString() === activeFilters.consolidation_id.toString());
      }
      if (activeFilters.age_range !== 'todos') {
        result = result.filter(p => {
          const age = calculateAge(p.birthdate);
          if (age === null) return false;
          if (activeFilters.age_range === 'jovenes') return age <= 25;
          if (activeFilters.age_range === 'adultos') return age >= 26 && age <= 50;
          if (activeFilters.age_range === 'mayores') return age >= 51;
          return true;
        });
      }

      result.sort((a, b) => {
        const lnA = (a.last_name || '').toLowerCase();
        const lnB = (b.last_name || '').toLowerCase();
        if (lnA !== lnB) return lnA.localeCompare(lnB);
        return (a.first_name || '').toLowerCase().localeCompare((b.first_name || '').toLowerCase());
      });

      if (isMounted) {
        setDisplayedPeople(result);
      }
    };

    applyFilters();

    return () => {
      isMounted = false;
    };
  }, [searchQuery, allPeople, activeFilters]);

  // --- MANEJO DE SELECCIÓN MEJORADO CON RESOLUCIÓN POR CATÁLOGO ---
  const handleSelectPerson = async (personId: string) => {
    if (expandedPersonId === personId) {
      setExpandedPersonId(null);
      setExpandedPersonData(null);
      setPersonDetails({ ministries: [], occupations: [] });
      return;
    }

    setExpandedPersonId(personId);
    setLoadingFilters(true);

    try {
      const [fullProfile, memberships, occupations] = await Promise.all([
        PeopleAPI.getPerson(personId),
        PeopleAPI.getPersonMemberships(personId).catch(() => []),
        PeopleAPI.getPersonOccupations(personId).catch(() => []),
      ]);

      setExpandedPersonData(fullProfile);

      const finalMinistries: any[] = Array.isArray(memberships)
        ? memberships.map((membership: any) => ({
            ...membership,
            name:
              membership.ministry?.name ||
              membership.ministry_name ||
              (typeof membership.ministry === 'string' ? membership.ministry : undefined) ||
              `Ministerio ID: ${membership.ministry_id || membership.ministry}`,
            area: membership.area || null,
          }))
        : [];

      const finalOccupations: any[] = Array.isArray(occupations)
        ? occupations.map((occupation: any) => ({
            ...occupation,
            name:
              occupation.name ||
              occupation.occupation_name ||
              occupation.occupation?.name ||
              (typeof occupation.occupation === 'string' ? occupation.occupation : undefined) ||
              `Ocupación ID: ${occupation.occupation_id || occupation.id}`,
          }))
        : [];

      setPersonDetails({
        ministries: finalMinistries.filter(Boolean),
        occupations: finalOccupations.filter(Boolean),
      });

    } catch (e) {
      console.log("Error cargando perfil completo:", e);
      setPersonDetails({ ministries: [], occupations: [] });
      setExpandedPersonData(null);
    } finally {
      setLoadingFilters(false);
    }
  };

  const clearAllFilters = () => {
    setActiveFilters({
      ministry: '', occupation: '', marital_status: '', membership_status: '',
      neighborhood: '', gender: '', baptized: '', cdb: '', consolidation_id: '', age_range: 'todos'
    });
    setSearchQuery('');
  };

  const activeFiltersCount = Object.values(activeFilters).filter(v => v !== '' && v !== 'todos').length;

  // --- TARJETAS RENDERS ---
  const renderPersonCard = ({ item }: any) => {
    const isExpanded = expandedPersonId?.toString() === (item.id || item.person_id)?.toString();
    const age = calculateAge(item.birthdate);

    const activeData = isExpanded && expandedPersonData ? expandedPersonData : item;

    const houseNumber = 
      activeData.address?.house_number || 
      activeData.address?.street_number || 
      activeData.address?.number || 
      activeData.address?.numero || 
      activeData.house_number || 
      activeData.street_number ||
      null;

    return (
      <View style={[styles.card, isExpanded && styles.cardExpanded]}>
        <TouchableOpacity onPress={() => handleSelectPerson(item.id || item.person_id)} activeOpacity={0.8}>
          <View style={styles.cardHeaderRow}>
            <View style={{ flex: 1 }}>
              <Text style={styles.personName}>{item.last_name?.toUpperCase()}, {item.first_name}</Text>
              <Text style={styles.personSubtitle}>
                ID: {item.person_id || item.id || '—'}  •  DNI: {item.dni || '---'}  •  {age ? `${age} años` : 'Sin edad registrado'}
              </Text>
            </View>
            <Text style={styles.expandIcon}>{isExpanded ? '▲' : '▼'}</Text>
          </View>
        </TouchableOpacity>

        {/* --- DESPLEGABLE CON TODOS LOS DATOS --- */}
        {isExpanded && (
          <View style={styles.expandedContent}>
            <View style={styles.divider} />
            <View style={{ flexDirection: 'row', justifyContent: 'flex-end', marginBottom: 8 }}>
              <TouchableOpacity style={[styles.toggleBtn, { paddingVertical: 8, paddingHorizontal: 12 }]} onPress={() => {
                const pid = (item.id || item.person_id);
                if (pid) router.push({ pathname: '/modify', params: { personId: pid } } as any);
              }}>
                <Text style={styles.toggleBtnText}>📝 Modificar</Text>
              </TouchableOpacity>
            </View>
            
            <Text style={styles.detailText}>📞 <Text style={styles.bold}>Teléfono:</Text> {activeData.phone_number || activeData.phone || 'No registrado'}</Text>
            <Text style={styles.detailText}>👤 <Text style={styles.bold}>Género:</Text> {activeData.gender || 'No registrado'}</Text>
            <Text style={styles.detailText}>� <Text style={styles.bold}>Correo:</Text> {activeData.email || 'No registrado'}</Text>
            <Text style={styles.detailText}>📅 <Text style={styles.bold}>Fecha de Nacimiento:</Text> {formatBirthdate(activeData.birthdate)}</Text>
            <Text style={styles.detailText}>⏳ <Text style={styles.bold}>Edad:</Text> {age ? `${age} años` : 'Sin registrar'}</Text>
            <Text style={styles.detailText}>🏡 <Text style={styles.bold}>Barrio:</Text> {activeData.address?.neighborhood || activeData.neighborhood || 'No registrado'}</Text>
            
            <Text style={styles.detailText}>
              📍 <Text style={styles.bold}>Calle:</Text>{' '}
              {activeData.address?.street || activeData.address?.street_name || activeData.street || 'No registrada'}
            </Text>
            <Text style={styles.detailText}>💍 <Text style={styles.bold}>Estado civil:</Text> {activeData.marital_status || 'No registrado'}</Text>
            <Text style={styles.detailText}>👥 <Text style={styles.bold}>Estado de membresía:</Text> {activeData.membership_status || 'No registrado'}</Text>
            <Text style={styles.detailText}>🆔 <Text style={styles.bold}>Obra social:</Text> {activeData.social_security || 'No registrado'}</Text>
            
            <Text style={styles.detailText}>
              🚪 <Text style={styles.bold}>Número de Casa:</Text>{' '}
              {houseNumber !== null && houseNumber !== undefined ? String(houseNumber) : 'S/N'}
            </Text>
            
            <Text style={styles.detailText}>📖 <Text style={styles.bold}>Casa de Bendición:</Text> {getCdbName(activeData.cdb || activeData.cdb_id)}</Text>
            <Text style={styles.detailText}>📈 <Text style={styles.bold}>Nivel de Consolidación:</Text> {getConsolidationLevel(activeData.consolidation_id || activeData.consolidation)}</Text>
            
            <Text style={styles.detailText}>
              💧 <Text style={styles.bold}>Bautismo:</Text>{' '}
              {activeData.baptized ? (
                <Text style={styles.textSuccess}>Sí, Bautizado</Text>
              ) : (
                <Text style={styles.textDanger}>No Bautizado</Text>
              )}
            </Text>

            {/* --- BLOQUE DE MINISTERIOS Y OCUPACIONES --- */}
            <View style={styles.toggleContainer}>
              <Text style={styles.sectionTabTitle}>
                {bottomViewMode === 'ministry' ? "⛪ Ministerios asignados" : "💼 Ocupaciones de la persona"}
              </Text>
              <TouchableOpacity 
                style={styles.toggleBtn}
                onPress={() => setBottomViewMode(prev => prev === 'ministry' ? 'occupation' : 'ministry')}
              >
                <Text style={styles.toggleBtnText}>Cambiar Vista ⇄</Text>
              </TouchableOpacity>
            </View>

            {loadingFilters ? (
              <ActivityIndicator size="small" color="#7A4A97" style={{ marginVertical: 10 }} />
            ) : bottomViewMode === 'ministry' ? (
              personDetails.ministries.length === 0 ? (
                <Text style={styles.subListEmpty}>Sin asignaciones de ministerio en la base de datos</Text>
              ) : (
                personDetails.ministries.map((m: any, idx: number) => (
                  <Text key={idx} style={styles.subListItem}>
                    • {m.name || m.ministry?.name || m.ministry_name || (typeof m === 'string' ? m : 'Ministerio Activo')} 
                    {m.area ? ` / Área: ${m.area.name || m.area.area || m.area}` : ''}
                  </Text>
                ))
              )
            ) : (
              personDetails.occupations.length === 0 ? (
                <Text style={styles.subListEmpty}>Sin ocupaciones registradas en la base de datos</Text>
              ) : (
                personDetails.occupations.map((o: any, idx: number) => (
                  <Text key={idx} style={styles.subListItem}>
                    • {o.name || o.occupation_name || o.occupation?.name || (typeof o === 'string' ? o : 'Ocupación registrada')}
                  </Text>
                ))
              )
            )}
          </View>
        )}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.headerTitle}>Buscador</Text>
      
      <View style={styles.searchContainerRow}>
        <TextInput
          style={styles.searchBar}
          placeholder="Buscar por nombre, apellido..."
          placeholderTextColor="#888"
          value={searchQuery}
          onChangeText={setSearchQuery}
        />
        <TouchableOpacity 
          style={[styles.filterButton, activeFiltersCount > 0 && styles.filterButtonActive]} 
          onPress={() => setIsFilterModalOpen(true)}
        >
          <Text style={styles.filterButtonText}>Filtros ▾ {activeFiltersCount > 0 ? `(${activeFiltersCount})` : ''}</Text>
        </TouchableOpacity>
      </View>

      {activeFiltersCount > 0 && (
        <TouchableOpacity style={styles.clearBadgeRow} onPress={clearAllFilters}>
          <Text style={styles.clearBadgeText}>Limpiar todos los filtros ✕</Text>
        </TouchableOpacity>
      )}

      <Text style={styles.resultsCounterText}>Resultados encontrados: {displayedPeople.length}</Text>

      {loading ? (
        <View style={styles.center}>
          <ActivityIndicator size="large" color="#7A4A97" />
          <Text style={styles.loadingText}>Sincronizando Base de Datos...</Text>
        </View>
      ) : (
        <FlatList
          data={displayedPeople}
          keyExtractor={(item, index) => (item.id || item.person_id || index).toString()}
          renderItem={renderPersonCard}
          contentContainerStyle={styles.listContainer}
          refreshing={refreshing}
          onRefresh={() => {
            setRefreshing(true);
            loadInitialData(false);
          }}
          ListEmptyComponent={
            <Text style={styles.emptyText}>No se encontraron personas con los filtros seleccionados.</Text>
          }
        />
      )}

      {/* --- MODAL DE FILTROS --- */}
      <Modal visible={isFilterModalOpen} animationType="slide" transparent={true}>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Filtros Avanzados</Text>
              <TouchableOpacity onPress={() => setIsFilterModalOpen(false)}>
                <Text style={styles.closeModalX}>✕</Text>
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.modalScroll}>
<Text style={styles.filterLabel}>Ministerio</Text>
            <View style={styles.pickerBox}>
              <Picker
                selectedValue={activeFilters.ministry}
                onValueChange={(v) => setActiveFilters(prev => ({ ...prev, ministry: v }))}
              >
                <Picker.Item label="[ Todos los ministerios ]" value="" />
                {filterCatalogs.ministries.map((m, i) => (
                  <Picker.Item key={i} label={m.name || `Ministerio ${m.ministry_id || m.id}`} value={(m.ministry_id || m.id).toString()} />
                ))}
              </Picker>
            </View>

            <Text style={styles.filterLabel}>Ocupación</Text>
            <View style={styles.pickerBox}>
              <Picker
                selectedValue={activeFilters.occupation}
                onValueChange={(v) => setActiveFilters(prev => ({ ...prev, occupation: v }))}
              >
                <Picker.Item label="[ Todas las ocupaciones ]" value="" />
                {filterCatalogs.occupations.map((o, i) => (
                  <Picker.Item key={i} label={o.name || `Ocupación ${o.occupation_id || o.id}`} value={(o.occupation_id || o.id).toString()} />
                ))}
              </Picker>
            </View>

            <Text style={styles.filterLabel}>Estado civil</Text>
            <View style={styles.pickerBox}>
              <Picker
                selectedValue={activeFilters.marital_status}
                onValueChange={(v) => setActiveFilters(prev => ({ ...prev, marital_status: v }))}
              >
                <Picker.Item label="Todos" value="" />
                {filterCatalogs.marital_statuses.map((status, i) => (
                  <Picker.Item key={i} label={status.name || status} value={status.name || status} />
                ))}
              </Picker>
            </View>

            <Text style={styles.filterLabel}>Estado de membresía</Text>
            <View style={styles.pickerBox}>
              <Picker
                selectedValue={activeFilters.membership_status}
                onValueChange={(v) => setActiveFilters(prev => ({ ...prev, membership_status: v }))}
              >
                <Picker.Item label="Todos" value="" />
                {filterCatalogs.membership_statuses.map((status, i) => (
                  <Picker.Item key={i} label={status.name || status} value={status.name || status} />
                ))}
              </Picker>
            </View>

            <Text style={styles.filterLabel}>Barrio</Text>
              <View style={styles.pickerBox}>
                <Picker
                  selectedValue={activeFilters.neighborhood}
                  onValueChange={(v) => setActiveFilters(prev => ({ ...prev, neighborhood: v }))}
                >
                  <Picker.Item label="[ Todos los barrios ]" value="" />
                  {filterCatalogs.neighborhoods.map((n, i) => (
                    <Picker.Item key={i} label={n} value={n} />
                  ))}
                </Picker>
              </View>

              <Text style={styles.filterLabel}>Rango de Edad</Text>
              <View style={styles.pickerBox}>
                <Picker
                  selectedValue={activeFilters.age_range}
                  onValueChange={(v) => setActiveFilters(prev => ({ ...prev, age_range: v }))}
                >
                  <Picker.Item label="Cualquier edad" value="todos" />
                  <Picker.Item label="Jóvenes (Hasta 25 años)" value="jovenes" />
                  <Picker.Item label="Adultos (26 a 50 años)" value="adultos" />
                  <Picker.Item label="Mayores (51 años o más)" value="mayores" />
                </Picker>
              </View>

              <Text style={styles.filterLabel}>Género</Text>
              <View style={styles.pickerBox}>
                <Picker
                  selectedValue={activeFilters.gender}
                  onValueChange={(v) => setActiveFilters(prev => ({ ...prev, gender: v }))}
                >
                  <Picker.Item label="Todos" value="" />
                  <Picker.Item label="Masculino" value="Masculino" />
                  <Picker.Item label="Femenino" value="Femenino" />
                </Picker>
              </View>

              <Text style={styles.filterLabel}>¿Bautizado?</Text>
              <View style={styles.pickerBox}>
                <Picker
                  selectedValue={activeFilters.baptized}
                  onValueChange={(v) => setActiveFilters(prev => ({ ...prev, baptized: v }))}
                >
                  <Picker.Item label="Todos" value="" />
                  <Picker.Item label="Sí" value="Sí" />
                  <Picker.Item label="No" value="No" />
                </Picker>
              </View>

              <Text style={styles.filterLabel}>¿Pertenece a CDB?</Text>
              <View style={styles.pickerBox}>
                <Picker
                  selectedValue={activeFilters.cdb}
                  onValueChange={(v) => setActiveFilters(prev => ({ ...prev, cdb: v }))}
                >
                  <Picker.Item label="Todos" value="" />
                  {filterCatalogs.cdbs.map((c: any, i) => (
                    <Picker.Item key={i} label={`CDB ${c.number || c.name}`} value={(c.id || c.cdb_id).toString()} />
                  ))}
                </Picker>
              </View>

              <Text style={styles.filterLabel}>Nivel de Consolidación</Text>
              <View style={styles.pickerBox}>
                <Picker
                  selectedValue={activeFilters.consolidation_id}
                  onValueChange={(v) => setActiveFilters(prev => ({ ...prev, consolidation_id: v }))}
                >
                  <Picker.Item label="Todos" value="" />
                  {filterCatalogs.consolidations.map((c: any, i) => (
                    <Picker.Item key={i} label={c.level || c.name} value={(c.id || c.consolidation_id).toString()} />
                  ))}
                </Picker>
              </View>
            </ScrollView>

            <TouchableOpacity style={styles.applyFiltersBtn} onPress={() => setIsFilterModalOpen(false)}>
              <Text style={styles.applyFiltersBtnText}>Aplicar Filtros Cruzados</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F0E6F6' },
  headerTitle: { fontSize: 18, fontWeight: 'bold', color: '#7A4A97', textAlign: 'center', marginVertical: 12 },
  searchContainerRow: { flexDirection: 'row', paddingHorizontal: 12, marginBottom: 5, alignItems: 'center' },
  searchBar: {
    flex: 1,
    backgroundColor: '#FFF',
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderRadius: 8,
    fontSize: 15,
    borderWidth: 1,
    borderColor: '#DDD',
    marginRight: 8
  },
  filterButton: { backgroundColor: '#7A4A97', paddingVertical: 11, paddingHorizontal: 12, borderRadius: 8 },
  filterButtonActive: { backgroundColor: '#A040A0' },
  filterButtonText: { color: '#FFF', fontWeight: 'bold', fontSize: 14 },
  clearBadgeRow: { alignSelf: 'center', backgroundColor: '#e74c3c', paddingVertical: 5, paddingHorizontal: 15, borderRadius: 15, marginVertical: 5 },
  clearBadgeText: { color: 'white', fontSize: 13, fontWeight: '600' },
  resultsCounterText: { fontSize: 13, color: '#5A5A5A', fontWeight: 'bold', marginLeft: 15, marginVertical: 4 },
  listContainer: { paddingHorizontal: 12, paddingBottom: 25 },
  
  card: {
    backgroundColor: '#FFF',
    padding: 14,
    borderRadius: 10,
    marginVertical: 5,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    elevation: 1
  },
  cardExpanded: { borderColor: '#7A4A97', borderWidth: 1.5 },
  cardHeaderRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  personName: { fontSize: 16, fontWeight: 'bold', color: '#333' },
  personSubtitle: { fontSize: 13, color: '#666', marginTop: 2 },
  expandIcon: { fontSize: 14, color: '#7A4A97', fontWeight: 'bold' },
  
  expandedContent: { marginTop: 12 },
  divider: { height: 1, backgroundColor: '#E2E8F0', marginBottom: 10 },
  detailText: { fontSize: 14, color: '#4A5568', marginVertical: 3.5 },
  bold: { fontWeight: '700', color: '#2D3748' },
  
  textSuccess: { color: '#2F855A', fontWeight: 'bold' },
  textDanger: { color: '#E53E3E', fontWeight: 'bold' },
  
  toggleContainer: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: 14, marginBottom: 8 },
  sectionTabTitle: { fontSize: 14, fontWeight: 'bold', color: '#7A4A97' },
  toggleBtn: { backgroundColor: '#E8DFEE', paddingVertical: 5, paddingHorizontal: 10, borderRadius: 6 },
  toggleBtnText: { color: '#7A4A97', fontSize: 12, fontWeight: 'bold' },
  subListItem: { fontSize: 14, color: '#333', paddingLeft: 10, paddingVertical: 3, fontWeight: '500' },
  subListEmpty: { fontSize: 13, color: '#999', fontStyle: 'italic', paddingLeft: 10 },

  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  loadingText: { marginTop: 10, color: '#5A5A5A', fontSize: 14 },
  emptyText: { textAlign: 'center', color: '#888', marginTop: 40, fontSize: 15 },

  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
  modalContent: { backgroundColor: 'white', borderTopLeftRadius: 20, borderTopRightRadius: 20, padding: 18, maxHeight: '80%' },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 15 },
  modalTitle: { fontSize: 18, fontWeight: 'bold', color: '#7A4A97' },
  closeModalX: { fontSize: 20, color: '#88', fontWeight: 'bold', padding: 4 },
  modalScroll: { marginBottom: 15 },
  filterLabel: { fontSize: 14, fontWeight: '600', color: '#5A5A5A', marginTop: 10, marginBottom: 4 },
  pickerBox: { backgroundColor: '#FFFBF5', borderWidth: 1, borderColor: '#DDD', borderRadius: 8, justifyContent: 'center' },
  applyFiltersBtn: { backgroundColor: '#7A4A97', padding: 14, borderRadius: 10, alignItems: 'center', marginBottom: 10 },
  applyFiltersBtnText: { color: 'white', fontSize: 16, fontWeight: 'bold' }
});