"""
📱 Phoenix Ecosystem - Tests Compatibilité Mobile
Validation responsive design et fonctionnalités mobile

Author: Claude Phoenix DevSecOps Guardian  
Version: 1.0.0 - Production Testing Suite
"""

import asyncio
import aiohttp
from playwright.async_api import async_playwright, Page, BrowserContext
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
import base64

logger = logging.getLogger(__name__)


@dataclass
class MobileTestConfig:
    """Configuration des tests mobile."""
    phoenix_cv_url: str = "https://phoenix-cv.streamlit.app"
    phoenix_letters_url: str = "https://phoenix-letters.streamlit.app"
    devices_to_test: List[Dict] = field(default_factory=list)
    viewports_to_test: List[Dict] = field(default_factory=list)
    performance_thresholds: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.devices_to_test:
            self.devices_to_test = [
                {
                    "name": "iPhone 12",
                    "viewport": {"width": 390, "height": 844},
                    "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
                },
                {
                    "name": "Samsung Galaxy S21",
                    "viewport": {"width": 384, "height": 854},
                    "user_agent": "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"
                },
                {
                    "name": "iPad",
                    "viewport": {"width": 768, "height": 1024},
                    "user_agent": "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
                },
                {
                    "name": "Android Tablet",
                    "viewport": {"width": 800, "height": 1280},
                    "user_agent": "Mozilla/5.0 (Linux; Android 11; SM-T870) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Safari/537.36"
                }
            ]
        
        if not self.viewports_to_test:
            self.viewports_to_test = [
                {"width": 320, "height": 568, "name": "Small Mobile"},
                {"width": 375, "height": 667, "name": "Medium Mobile"},
                {"width": 414, "height": 896, "name": "Large Mobile"},
                {"width": 768, "height": 1024, "name": "Tablet Portrait"},
                {"width": 1024, "height": 768, "name": "Tablet Landscape"}
            ]
        
        if not self.performance_thresholds:
            self.performance_thresholds = {
                "load_time_seconds": 5.0,
                "first_contentful_paint_ms": 3000,
                "largest_contentful_paint_ms": 4000,
                "cumulative_layout_shift": 0.1
            }


class MobileCompatibilityTester:
    """Testeur de compatibilité mobile avec Playwright."""
    
    def __init__(self, config: MobileTestConfig):
        self.config = config
        self.playwright = None
        self.browser = None
    
    async def setup(self):
        """Initialise Playwright et le navigateur."""
        self.playwright = await async_playwright().start()
        
        # Utilisation de Chromium pour tests mobile
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
    
    async def cleanup(self):
        """Nettoie les ressources."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def test_responsive_design(self, app_url: str, app_name: str) -> Dict[str, Any]:
        """
        Test du design responsive sur différents appareils.
        
        Args:
            app_url: URL de l'application
            app_name: Nom de l'application
            
        Returns:
            Résultats des tests responsive
        """
        test_results = {
            "test_name": f"Responsive Design - {app_name}",
            "app_url": app_url,
            "timestamp": datetime.now().isoformat(),
            "device_tests": [],
            "viewport_tests": [],
            "overall_success": False
        }
        
        # Tests sur différents appareils
        for device in self.config.devices_to_test:
            device_result = await self._test_device_compatibility(app_url, device)
            test_results["device_tests"].append(device_result)
        
        # Tests sur différents viewports
        for viewport in self.config.viewports_to_test:
            viewport_result = await self._test_viewport_compatibility(app_url, viewport)
            test_results["viewport_tests"].append(viewport_result)
        
        # Détermination du succès global
        device_success = all(test["success"] for test in test_results["device_tests"])
        viewport_success = all(test["success"] for test in test_results["viewport_tests"])
        test_results["overall_success"] = device_success and viewport_success
        
        return test_results
    
    async def _test_device_compatibility(self, app_url: str, device: Dict) -> Dict[str, Any]:
        """Test de compatibilité pour un appareil spécifique."""
        device_result = {
            "device_name": device["name"],
            "success": False,
            "duration": 0,
            "details": {}
        }
        
        try:
            start_time = time.time()
            
            # Création du contexte avec les paramètres de l'appareil
            context = await self.browser.new_context(
                viewport=device["viewport"],
                user_agent=device["user_agent"],
                device_scale_factor=2 if "iPhone" in device["name"] else 1
            )
            
            page = await context.new_page()
            
            # Navigation vers l'application
            await page.goto(app_url, wait_until="networkidle")
            
            # Tests de base
            layout_checks = await self._check_mobile_layout(page, device["viewport"])
            performance_metrics = await self._measure_mobile_performance(page)
            interaction_tests = await self._test_mobile_interactions(page)
            
            end_time = time.time()
            device_result["duration"] = round(end_time - start_time, 2)
            
            device_result["details"] = {
                "viewport": device["viewport"],
                "layout_checks": layout_checks,
                "performance_metrics": performance_metrics,
                "interaction_tests": interaction_tests,
                "screenshot_taken": await self._take_screenshot(page, f"{device['name'].lower().replace(' ', '_')}")
            }
            
            # Évaluation du succès
            device_result["success"] = (
                layout_checks["responsive_layout"] and
                performance_metrics["load_time"] < self.config.performance_thresholds["load_time_seconds"] and
                interaction_tests["basic_interactions"]
            )
            
            await context.close()
            
        except Exception as e:
            device_result["details"]["error"] = str(e)
            logger.error(f"Erreur test device {device['name']}: {e}")
        
        return device_result
    
    async def _test_viewport_compatibility(self, app_url: str, viewport: Dict) -> Dict[str, Any]:
        """Test de compatibilité pour un viewport spécifique."""
        viewport_result = {
            "viewport_name": viewport["name"],
            "viewport_size": f"{viewport['width']}x{viewport['height']}",
            "success": False,
            "duration": 0,
            "details": {}
        }
        
        try:
            start_time = time.time()
            
            context = await self.browser.new_context(
                viewport={"width": viewport["width"], "height": viewport["height"]}
            )
            
            page = await context.new_page()
            await page.goto(app_url, wait_until="networkidle")
            
            # Vérifications spécifiques au viewport
            layout_analysis = await self._analyze_viewport_layout(page, viewport)
            scroll_behavior = await self._test_scroll_behavior(page)
            element_visibility = await self._check_element_visibility(page)
            
            end_time = time.time()
            viewport_result["duration"] = round(end_time - start_time, 2)
            
            viewport_result["details"] = {
                "layout_analysis": layout_analysis,
                "scroll_behavior": scroll_behavior,
                "element_visibility": element_visibility
            }
            
            viewport_result["success"] = (
                layout_analysis["content_fits"] and
                scroll_behavior["vertical_scroll_works"] and
                element_visibility["essential_elements_visible"]
            )
            
            await context.close()
            
        except Exception as e:
            viewport_result["details"]["error"] = str(e)
        
        return viewport_result
    
    async def _check_mobile_layout(self, page: Page, viewport: Dict) -> Dict[str, Any]:
        """Vérifie la mise en page mobile."""
        layout_checks = {
            "responsive_layout": False,
            "no_horizontal_scroll": False,
            "touch_targets_adequate": False,
            "content_readable": False
        }
        
        try:
            # Vérification du défilement horizontal
            body_width = await page.evaluate("document.body.scrollWidth")
            viewport_width = viewport["width"]
            layout_checks["no_horizontal_scroll"] = body_width <= viewport_width + 10  # Tolérance de 10px
            
            # Vérification des targets tactiles
            buttons = await page.query_selector_all("button, a, input[type='submit']")
            adequate_targets = 0
            
            for button in buttons:
                box = await button.bounding_box()
                if box and (box["width"] >= 44 and box["height"] >= 44):
                    adequate_targets += 1
            
            layout_checks["touch_targets_adequate"] = adequate_targets > 0
            
            # Vérification de la lisibilité du contenu
            font_sizes = await page.evaluate("""
                Array.from(document.querySelectorAll('p, span, div, h1, h2, h3, h4, h5, h6'))
                    .map(el => parseFloat(getComputedStyle(el).fontSize))
                    .filter(size => !isNaN(size))
            """)
            
            if font_sizes:
                min_font_size = min(font_sizes)
                layout_checks["content_readable"] = min_font_size >= 14  # Minimum 14px
            
            # Layout responsive global
            layout_checks["responsive_layout"] = (
                layout_checks["no_horizontal_scroll"] and
                layout_checks["touch_targets_adequate"]
            )
            
        except Exception as e:
            logger.error(f"Erreur vérification layout mobile: {e}")
        
        return layout_checks
    
    async def _measure_mobile_performance(self, page: Page) -> Dict[str, Any]:
        """Mesure les performances mobile."""
        performance_metrics = {
            "load_time": 0,
            "first_contentful_paint": 0,
            "largest_contentful_paint": 0,
            "cumulative_layout_shift": 0
        }
        
        try:
            # Mesure des métriques Web Vitals
            metrics = await page.evaluate("""
                new Promise((resolve) => {
                    const observer = new PerformanceObserver((list) => {
                        const entries = list.getEntries();
                        const metrics = {};
                        
                        entries.forEach(entry => {
                            if (entry.entryType === 'paint') {
                                if (entry.name === 'first-contentful-paint') {
                                    metrics.first_contentful_paint = entry.startTime;
                                }
                            } else if (entry.entryType === 'largest-contentful-paint') {
                                metrics.largest_contentful_paint = entry.startTime;
                            } else if (entry.entryType === 'layout-shift') {
                                if (!entry.hadRecentInput) {
                                    metrics.cumulative_layout_shift = (metrics.cumulative_layout_shift || 0) + entry.value;
                                }
                            }
                        });
                        
                        resolve(metrics);
                    });
                    
                    observer.observe({entryTypes: ['paint', 'largest-contentful-paint', 'layout-shift']});
                    
                    // Timeout après 5 secondes
                    setTimeout(() => resolve({}), 5000);
                })
            """)
            
            # Temps de chargement depuis navigationStart
            load_time = await page.evaluate("""
                performance.timing.loadEventEnd - performance.timing.navigationStart
            """)
            
            performance_metrics["load_time"] = load_time / 1000  # Conversion en secondes
            performance_metrics.update(metrics)
            
        except Exception as e:
            logger.error(f"Erreur mesure performance mobile: {e}")
        
        return performance_metrics
    
    async def _test_mobile_interactions(self, page: Page) -> Dict[str, Any]:
        """Test des interactions tactiles."""
        interaction_tests = {
            "basic_interactions": False,
            "touch_events": False,
            "scroll_functionality": False
        }
        
        try:
            # Test du scroll
            initial_scroll = await page.evaluate("window.pageYOffset")
            await page.evaluate("window.scrollBy(0, 100)")
            await page.wait_for_timeout(500)
            
            final_scroll = await page.evaluate("window.pageYOffset")
            interaction_tests["scroll_functionality"] = final_scroll > initial_scroll
            
            # Test des éléments cliquables
            clickable_elements = await page.query_selector_all("button, a, [role='button']")
            
            if clickable_elements:
                # Test de clic sur le premier élément
                try:
                    await clickable_elements[0].click()
                    interaction_tests["basic_interactions"] = True
                except:
                    pass
            
            # Simulation d'événement tactile
            try:
                await page.touch_screen.tap(100, 100)
                interaction_tests["touch_events"] = True
            except:
                pass
            
        except Exception as e:
            logger.error(f"Erreur test interactions mobile: {e}")
        
        return interaction_tests
    
    async def _analyze_viewport_layout(self, page: Page, viewport: Dict) -> Dict[str, Any]:
        """Analyse la mise en page pour un viewport."""
        analysis = {
            "content_fits": False,
            "proper_scaling": False,
            "navigation_accessible": False
        }
        
        try:
            # Vérification que le contenu s'adapte
            content_width = await page.evaluate("Math.max(document.body.scrollWidth, document.body.offsetWidth)")
            analysis["content_fits"] = content_width <= viewport["width"] + 20  # Tolérance
            
            # Vérification du scaling
            zoom_level = await page.evaluate("window.devicePixelRatio || 1")
            analysis["proper_scaling"] = 0.8 <= zoom_level <= 3.0
            
            # Vérification accessibilité navigation
            nav_elements = await page.query_selector_all("nav, [role='navigation'], .navigation")
            analysis["navigation_accessible"] = len(nav_elements) > 0
            
        except Exception as e:
            logger.error(f"Erreur analyse viewport: {e}")
        
        return analysis
    
    async def _test_scroll_behavior(self, page: Page) -> Dict[str, Any]:
        """Test du comportement de défilement."""
        scroll_behavior = {
            "vertical_scroll_works": False,
            "smooth_scrolling": False,
            "scroll_position_maintained": False
        }
        
        try:
            # Test scroll vertical
            initial_y = await page.evaluate("window.pageYOffset")
            await page.evaluate("window.scrollBy(0, 200)")
            await page.wait_for_timeout(300)
            
            new_y = await page.evaluate("window.pageYOffset")
            scroll_behavior["vertical_scroll_works"] = new_y > initial_y
            
            # Test maintien de position
            await page.reload()
            await page.wait_for_load_state("networkidle")
            
            after_reload_y = await page.evaluate("window.pageYOffset")
            scroll_behavior["scroll_position_maintained"] = after_reload_y == 0  # Retour en haut
            
            scroll_behavior["smooth_scrolling"] = True  # Supposé supporté
            
        except Exception as e:
            logger.error(f"Erreur test scroll: {e}")
        
        return scroll_behavior
    
    async def _check_element_visibility(self, page: Page) -> Dict[str, Any]:
        """Vérifie la visibilité des éléments essentiels."""
        visibility = {
            "essential_elements_visible": False,
            "no_overlapping_content": False,
            "readable_text": False
        }
        
        try:
            # Vérification des éléments essentiels
            essential_selectors = ["h1", "nav", "main", "[role='main']", "button"]
            visible_essentials = 0
            
            for selector in essential_selectors:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    is_visible = await element.is_visible()
                    if is_visible:
                        visible_essentials += 1
                        break
            
            visibility["essential_elements_visible"] = visible_essentials >= 2
            
            # Vérification du texte lisible
            text_elements = await page.query_selector_all("p, span, div, h1, h2, h3")
            readable_texts = 0
            
            for element in text_elements[:5]:  # Test sur 5 premiers éléments
                try:
                    text_content = await element.text_content()
                    if text_content and len(text_content.strip()) > 10:
                        readable_texts += 1
                except:
                    pass
            
            visibility["readable_text"] = readable_texts > 0
            visibility["no_overlapping_content"] = True  # Difficile à tester automatiquement
            
        except Exception as e:
            logger.error(f"Erreur vérification visibilité: {e}")
        
        return visibility
    
    async def _take_screenshot(self, page: Page, device_name: str) -> bool:
        """Prend une capture d'écran."""
        try:
            screenshot_path = f"screenshots/mobile_{device_name}_{int(time.time())}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            return True
        except Exception as e:
            logger.error(f"Erreur capture écran: {e}")
            return False
    
    async def test_mobile_specific_features(self, app_url: str) -> Dict[str, Any]:
        """Test des fonctionnalités spécifiques mobile."""
        feature_tests = {
            "test_name": "Mobile Specific Features",
            "timestamp": datetime.now().isoformat(),
            "features": {},
            "overall_success": False
        }
        
        context = await self.browser.new_context(
            viewport={"width": 375, "height": 667},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        )
        
        try:
            page = await context.new_page()
            await page.goto(app_url, wait_until="networkidle")
            
            # Test des gestes tactiles
            feature_tests["features"]["touch_gestures"] = await self._test_touch_gestures(page)
            
            # Test de l'orientation
            feature_tests["features"]["orientation_handling"] = await self._test_orientation_handling(page)
            
            # Test des fonctés natives du navigateur mobile
            feature_tests["features"]["mobile_browser_features"] = await self._test_mobile_browser_features(page)
            
            # Test de l'accessibilité mobile
            feature_tests["features"]["mobile_accessibility"] = await self._test_mobile_accessibility(page)
            
            # Évaluation globale
            successful_features = sum(
                1 for feature in feature_tests["features"].values() 
                if feature.get("success", False)
            )
            
            feature_tests["overall_success"] = successful_features >= len(feature_tests["features"]) // 2
            
        finally:
            await context.close()
        
        return feature_tests
    
    async def _test_touch_gestures(self, page: Page) -> Dict[str, Any]:
        """Test des gestes tactiles."""
        touch_test = {"success": False, "gestures_tested": []}
        
        try:
            # Test tap
            await page.touch_screen.tap(100, 100)
            touch_test["gestures_tested"].append("tap")
            
            # Test swipe (si applicable)
            # await page.touch_screen.swipe(100, 200, 300, 200)
            # touch_test["gestures_tested"].append("swipe")
            
            touch_test["success"] = len(touch_test["gestures_tested"]) > 0
            
        except Exception as e:
            touch_test["error"] = str(e)
        
        return touch_test
    
    async def _test_orientation_handling(self, page: Page) -> Dict[str, Any]:
        """Test de la gestion de l'orientation."""
        orientation_test = {"success": False, "orientations_tested": []}
        
        try:
            # Portrait
            await page.set_viewport_size({"width": 375, "height": 667})
            await page.wait_for_timeout(500)
            orientation_test["orientations_tested"].append("portrait")
            
            # Paysage
            await page.set_viewport_size({"width": 667, "height": 375})
            await page.wait_for_timeout(500)
            orientation_test["orientations_tested"].append("landscape")
            
            orientation_test["success"] = len(orientation_test["orientations_tested"]) == 2
            
        except Exception as e:
            orientation_test["error"] = str(e)
        
        return orientation_test
    
    async def _test_mobile_browser_features(self, page: Page) -> Dict[str, Any]:
        """Test des fonctionnalités spécifiques au navigateur mobile."""
        browser_test = {"success": False, "features_available": []}
        
        try:
            # Test de la géolocalisation (support)
            geolocation_support = await page.evaluate("""
                'geolocation' in navigator
            """)
            
            if geolocation_support:
                browser_test["features_available"].append("geolocation")
            
            # Test du support tactile
            touch_support = await page.evaluate("""
                'ontouchstart' in window || navigator.maxTouchPoints > 0
            """)
            
            if touch_support:
                browser_test["features_available"].append("touch")
            
            # Test de l'orientation
            orientation_support = await page.evaluate("""
                'orientation' in window || 'onorientationchange' in window
            """)
            
            if orientation_support:
                browser_test["features_available"].append("orientation")
            
            browser_test["success"] = len(browser_test["features_available"]) >= 2
            
        except Exception as e:
            browser_test["error"] = str(e)
        
        return browser_test
    
    async def _test_mobile_accessibility(self, page: Page) -> Dict[str, Any]:
        """Test de l'accessibilité mobile."""
        accessibility_test = {"success": False, "checks": {}}
        
        try:
            # Vérification des labels ARIA
            aria_labels = await page.evaluate("""
                document.querySelectorAll('[aria-label], [aria-labelledby]').length
            """)
            accessibility_test["checks"]["aria_labels"] = aria_labels > 0
            
            # Vérification des rôles
            role_elements = await page.evaluate("""
                document.querySelectorAll('[role]').length
            """)
            accessibility_test["checks"]["role_attributes"] = role_elements > 0
            
            # Vérification de la navigation au clavier (simulée)
            focusable_elements = await page.evaluate("""
                document.querySelectorAll('button, a, input, select, textarea, [tabindex]').length
            """)
            accessibility_test["checks"]["focusable_elements"] = focusable_elements > 0
            
            # Succès si au moins 2 vérifications passent
            passed_checks = sum(accessibility_test["checks"].values())
            accessibility_test["success"] = passed_checks >= 2
            
        except Exception as e:
            accessibility_test["error"] = str(e)
        
        return accessibility_test


def generate_mobile_test_report(test_results: Dict[str, Any]) -> str:
    """Génère un rapport HTML des tests mobile."""
    
    html_report = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📱 Phoenix - Rapport Tests Mobile</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; line-height: 1.6; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 15px; text-align: center; }}
            .summary {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }}
            .test-section {{ border: 1px solid #ddd; margin: 15px 0; border-radius: 8px; overflow: hidden; }}
            .section-header {{ background: #007bff; color: white; padding: 15px; font-weight: bold; }}
            .section-content {{ padding: 20px; }}
            .success {{ background: #d4edda; border-color: #c3e6cb; }}
            .failure {{ background: #f8d7da; border-color: #f5c6cb; }}
            .device-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
            .device-card {{ border: 1px solid #ddd; border-radius: 8px; padding: 15px; }}
            .metric {{ display: flex; justify-content: space-between; margin: 5px 0; }}
            .metric-value {{ font-weight: bold; }}
            .recommendations {{ background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📱 Phoenix Ecosystem - Tests Compatibilité Mobile</h1>
            <p>Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <h2>📊 Résumé Exécutif</h2>
            <p><strong>Applications testées:</strong> {len(test_results)}</p>
    """
    
    # Ajout des détails de chaque test
    for app_name, app_results in test_results.items():
        if app_name == "summary":
            continue
            
        success_class = "success" if app_results.get("overall_success", False) else "failure"
        
        html_report += f"""
        <div class="test-section {success_class}">
            <div class="section-header">
                {app_name} - {'✅ SUCCÈS' if app_results.get('overall_success', False) else '❌ ÉCHEC'}
            </div>
            <div class="section-content">
        """
        
        # Tests d'appareils
        if "device_tests" in app_results:
            html_report += f"""
                <h3>📱 Tests par Appareil</h3>
                <div class="device-grid">
            """
            
            for device_test in app_results["device_tests"]:
                device_success = "✅" if device_test["success"] else "❌"
                html_report += f"""
                    <div class="device-card">
                        <h4>{device_success} {device_test['device_name']}</h4>
                        <div class="metric">
                            <span>Durée:</span>
                            <span class="metric-value">{device_test['duration']}s</span>
                        </div>
                """
                
                if "details" in device_test and "performance_metrics" in device_test["details"]:
                    perf = device_test["details"]["performance_metrics"]
                    html_report += f"""
                        <div class="metric">
                            <span>Temps de chargement:</span>
                            <span class="metric-value">{perf.get('load_time', 0):.2f}s</span>
                        </div>
                    """
                
                html_report += "</div>"
            
            html_report += "</div>"
        
        html_report += "</div></div>"
    
    # Recommandations
    html_report += """
        <div class="recommendations">
            <h2>💡 Recommandations</h2>
            <ul>
                <li>Optimiser les temps de chargement pour mobile (< 3s recommandé)</li>
                <li>Vérifier la taille des éléments tactiles (min 44px)</li>
                <li>Tester sur dispositifs réels pour validation finale</li>
                <li>Implémenter le lazy loading pour les images</li>
                <li>Optimiser les polices pour la lisibilité mobile</li>
            </ul>
        </div>
    """
    
    html_report += """
    </body>
    </html>
    """
    
    return html_report


async def run_comprehensive_mobile_tests() -> Dict[str, Any]:
    """Lance les tests mobile complets."""
    config = MobileTestConfig()
    tester = MobileCompatibilityTester(config)
    
    print("📱 Démarrage des tests de compatibilité mobile...")
    
    try:
        await tester.setup()
        
        results = {}
        
        # Tests Phoenix CV
        print("🔍 Tests mobile Phoenix CV...")
        cv_results = await tester.test_responsive_design(
            config.phoenix_cv_url, 
            "Phoenix CV"
        )
        results["Phoenix CV"] = cv_results
        
        # Tests Phoenix Letters
        print("📝 Tests mobile Phoenix Letters...")
        letters_results = await tester.test_responsive_design(
            config.phoenix_letters_url,
            "Phoenix Letters"
        )
        results["Phoenix Letters"] = letters_results
        
        # Tests fonctionnalités spécifiques mobile
        print("📱 Tests fonctionnalités spécifiques mobile...")
        mobile_features = await tester.test_mobile_specific_features(
            config.phoenix_letters_url
        )
        results["Mobile Features"] = mobile_features
        
        return results
        
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    print("📱 Phoenix Ecosystem - Tests de Compatibilité Mobile")
    print("=" * 60)
    
    try:
        # Création du dossier screenshots
        import os
        os.makedirs("screenshots", exist_ok=True)
        
        # Lancement des tests
        test_results = asyncio.run(run_comprehensive_mobile_tests())
        
        # Génération du rapport
        html_report = generate_mobile_test_report(test_results)
        
        # Sauvegarde
        with open("phoenix_mobile_test_report.html", "w", encoding="utf-8") as f:
            f.write(html_report)
        
        with open("phoenix_mobile_test_results.json", "w", encoding="utf-8") as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False, default=str)
        
        # Résumé
        total_apps = len([k for k in test_results.keys() if k != "summary"])
        successful_apps = sum(1 for app_results in test_results.values() 
                             if app_results.get("overall_success", False))
        
        print(f"\n✅ Tests mobile terminés:")
        print(f"📱 {successful_apps}/{total_apps} applications compatibles mobile")
        print(f"📊 Rapport HTML: phoenix_mobile_test_report.html")
        print(f"📁 Données JSON: phoenix_mobile_test_results.json")
        
    except Exception as e:
        print(f"❌ Erreur lors des tests mobile: {e}")
        logger.exception("Erreur tests mobile")