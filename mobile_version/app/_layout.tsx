import FontAwesome from '@expo/vector-icons/FontAwesome';
import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { useFonts } from 'expo-font';
import { Stack } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect } from 'react';
import { Alert, Platform } from 'react-native'; 
import 'react-native-reanimated';

// Importamos las librerías nativas para manejar la actualización
import * as Application from 'expo-application';
import * as IntentLauncher from 'expo-intent-launcher';

// ✅ TRUCO FINAL DE TYPESCRIPT: 
// Importamos el módulo por defecto como 'ExpoFileSystem' y lo renombramos abajo para burlar el error de tipos.
import ExpoFileSystem from 'expo-file-system';
const FileSystem: any = ExpoFileSystem;

// Importamos tu cliente de API modificado
import { ApiClient } from '../api/api_client'; 

import { useColorScheme } from '@/components/useColorScheme';

export {
  // Catch any errors thrown by the Layout component.
  ErrorBoundary,
} from 'expo-router';

export const unstable_settings = {
  // Ensure that reloading on `/modal` keeps a back button present.
  initialRouteName: '(tabs)',
};

// Prevent the splash screen from auto-hiding before asset loading is complete.
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [loaded, error] = useFonts({
    SpaceMono: require('../assets/fonts/SpaceMono-Regular.ttf'),
    ...FontAwesome.font,
  });

  // Expo Router uses Error Boundaries to catch errors in the navigation tree.
  useEffect(() => {
    if (error) throw error;
  }, [error]);

  useEffect(() => {
    if (loaded) {
      SplashScreen.hideAsync();
    }
  }, [loaded]);

  if (!loaded) {
    return null;
  }

  return <RootLayoutNav />;
}

function RootLayoutNav() {
  const colorScheme = useColorScheme();

  // 🚀 LÓGICA DE AUTO-UPDATE INTEGRADA
  useEffect(() => {
    // Solo ejecutamos el chequeo si es un dispositivo Android real o emulador
    if (Platform.OS === 'android') {
      ejecutarChequeoDeVersion();
    }
  }, []);

  const ejecutarChequeoDeVersion = async () => {
    try {
      // 1. Obtener la versión actual instalada (lee el 'version' de tu app.json)
      const versionActual = Application.nativeApplicationVersion;

      // 2. Consultar a tu servidor en Render
      const datosServidor = await ApiClient.checkMobileVersion();
      if (!datosServidor) return; // Si el servidor falla o no hay internet, no frena la app

      const { latestVersion, downloadUrl } = datosServidor;

      // 3. Comparar versiones
      if (versionActual !== latestVersion && downloadUrl) {
        Alert.alert(
          "¡Nueva versión disponible!",
          `Hay una actualización disponible (v${latestVersion}). ¿Querés instalarla ahora para tener las últimas mejoras?`,
          [
            { text: "Más tarde", style: "cancel" },
            { 
              text: "Actualizar", 
              onPress: () => descargarEInstalarApk(downloadUrl) 
            }
          ]
        );
      }
    } catch (err) {
      console.error("Error en el flujo de verificación de versión móvil:", err);
    }
  };

  const descargarEInstalarApk = async (urlDeGitHub: string) => {
    try {
      Alert.alert("Descargando", "La actualización se está bajando desde GitHub, aguarda un momento...");

      const nombreArchivo = "renuevo_update.apk";
      
      // ✅ Volvemos a usar el formato original que lee los métodos dinámicamente
      const rutaDestino = `${FileSystem.cacheDirectory}${nombreArchivo}`;

      // 4. Descargar el archivo pesado desde los servidores de GitHub (Gratis)
      const resultadoDescarga = await FileSystem.downloadAsync(urlDeGitHub, rutaDestino);

      if (resultadoDescarga.status === 200) {
        const contentUri = await FileSystem.getContentUriAsync(resultadoDescarga.uri);

        // 5. Lanzar el instalador de paquetes nativo de Android
        await IntentLauncher.startActivityAsync('android.intent.action.INSTALL_PACKAGE', {
          data: contentUri,
          flags: 1, // Da permisos de lectura temporales para abrir el APK
          type: 'application/vnd.android.package-archive'
        });
      } else {
        Alert.alert("Error de descarga", "No se pudo obtener el archivo desde GitHub.");
      }
    } catch (error) {
      console.error("Error al intentar instalar el APK:", error);
      Alert.alert(
        "Error de instalación", 
        "Hubo un problema. Si es la primera vez, asegúrate de dar permisos para instalar aplicaciones desconocidas si el sistema lo solicita."
      );
    }
  };

  return (
    <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
      <Stack>
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="modal" options={{ presentation: 'modal' }} />
      </Stack>
    </ThemeProvider>
  );
}